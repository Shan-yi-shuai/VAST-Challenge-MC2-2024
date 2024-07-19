<script setup lang='ts'>
import { storeToRefs } from 'pinia'
import * as d3 from 'd3'
import { watch } from 'vue'
import { useStore } from '../stores/store'
import { on } from 'events';

interface VesselMovement {
  date: string | Date
  vessel_id: string
  location_id: string
}

interface TransportMovement {
  date: string | Date
  vessel_id: string
  location_id: string
  key: string
}

const {
  width,
  height,
} = defineProps({
  width: { default: 1500, type: Number },
  height: { default: 900, type: Number },
})

// acquire pinia store
const store = useStore()
const { harborMovements, transportMovements, commodityDistributions, selectedVesselIDs, selectedLocationIDs, selectedCommodityIDs, dateInterval, vesselID2Vessel, focusVesselID, vesselTypeColor, locationColor, vesselID2Name, locationID2Name } = storeToRefs(store)

function renderChart(originalTransportMovements: any, originalCommodityDistributions: any, focusVesselID: any, selectedVesselIDs: any, selectedLocationIDs: any, selectedCommodityIDs: any, dateInterval: any): void {
  const transportMovements = originalTransportMovements.filter((d: any) => selectedVesselIDs.includes(d.vessel_id)).filter((d: any) => selectedLocationIDs.includes(d.location_id)).filter((d: any) => d3.timeParse('%Y-%m-%d')(dateInterval[0]) <= d3.timeParse('%Y-%m-%dT%H:%M:%S')(d.date) && d3.timeParse('%Y-%m-%dT%H:%M:%S')(d.date) <= d3.timeParse('%Y-%m-%d')(dateInterval[1]))
  const transportMovementsCopy = JSON.parse(JSON.stringify(transportMovements))

  const parseDate1 = d3.timeParse('%Y-%m-%dT%H:%M:%S')

  transportMovementsCopy.forEach((d: any) => {
    d.date = parseDate1(d.date)
  })

  const vesselIDTypes = []

  for (const key of selectedVesselIDs) {
    const vessel = vesselID2Vessel.value[key]
    vesselIDTypes.push({ vessel_id: vessel.id, vessel_type: vessel.type })
  }

  // 按类型对数据进行分组
  const grouped_data = d3.group(vesselIDTypes, (d: any) => d.vessel_type)

  // 将分组后的数据平铺为一个数组
  const sorted_vessel_data: any[] = []
  grouped_data.forEach((group: any) => {
    sorted_vessel_data.push(...group)
  })

  const index = sorted_vessel_data.findIndex(item => item.vessel_id === focusVesselID)

  // 如果值不存在于列表中，直接返回原列表
  if (index !== -1) {
    const [item] = sorted_vessel_data.splice(index, 1)
    sorted_vessel_data.unshift(item)
  }

  const margin = { top: 10, right: 10, bottom: 10, left: 20 }
  const _width = width - margin.left - margin.right
  const _height = height - margin.top - margin.bottom

  d3.select('#chart1').selectAll('*').remove()
  const svg = d3.select('#chart1')
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // 设置时间轴范围
  const x = d3.scaleTime()
    .domain(dateInterval.map((d: string) => d3.timeParse('%Y-%m-%d')(d)) as [Date, Date])
    .range([0, _width - 40])

  const yVessel = d3.scaleBand()
    .domain(sorted_vessel_data.map((d: TransportMovement) => d.vessel_id))
    .range([0, _height - 10])
    .padding(0.1)

  const barWidth = x(new Date(d3.timeDay.offset(x.domain()[0], 1))) - x(x.domain()[0])

  // 绘制时间轴
  svg.append('g')
    .attr('transform', `translate(0,${_height - 10})`)
    .call(d3.axisBottom(x).tickFormat(d3.timeFormat('%Y-%m-%d')))
    .selectAll('text') // 选择所有文本标签
    .style('font-size', '6px') // 设置字体大小为10px

  // 绘制y轴并根据vessel_type设置文本颜色
  const yAxis = svg.append('g')
    .call(d3.axisLeft(yVessel))

  yAxis.selectAll('text')
    .style('fill', d => {
      const vessel = sorted_vessel_data.find(v => v.vessel_id === d)
      return vessel ? vesselTypeColor.value(vessel.vessel_type) : 'black'
    })
    .text(d => vesselID2Name.value[d] || d)
    .attr('font-size', 3)

  // Tooltip div
  const tooltip = d3.select('body')
    .append('div')
    .style('position', 'absolute')
    .style('background', '#fff')
    .style('border', '1px solid #000')
    .style('padding', '5px')
    .style('display', 'none')
    .style('pointer-events', 'none')

  // 绘制上半部分的vessel
  svg.selectAll('.vessel')
    .data(transportMovementsCopy)
    .enter().append('rect')
    .attr('class', 'bar vessel')
    .attr('x', (d: TransportMovement) => x(d.date as Date))
    .attr('y', (d: TransportMovement) => yVessel(d.vessel_id) as number)
    .attr('width', barWidth) // 占至少一天的长度
    .attr('height', yVessel.bandwidth())
    .attr('fill', (d: VesselMovement) => locationColor.value(d.location_id))
    .attr('stroke', 'none')
    .on('mouseover', function (event, d: TransportMovement) {
      tooltip.style('display', 'block')
        .html(`Vessel: ${vesselID2Name.value[d.vessel_id]}<br>Date: ${d3.timeFormat('%Y-%m-%d')(d.date as Date)}<br>Location: ${locationID2Name.value[d.location_id]}`)
      d3.select(this).classed('box', true)
    })
    .on('mousemove', (event) => {
      const [svgX, svgY] = d3.pointer(event)
      const tooltipWidth = tooltip.node().offsetWidth
      const tooltipHeight = tooltip.node().offsetHeight
      const svgBounds = svg.node().getBoundingClientRect()
      let left = svgX + svgBounds.left + 10
      let top = svgY + svgBounds.top + 10

      // Adjust to keep the tooltip within SVG bounds
      if (left + tooltipWidth > svgBounds.right)
        left = left - tooltipWidth - 20
      if (top + tooltipHeight > svgBounds.bottom)
        top = top - tooltipHeight - 20

      tooltip.style('left', `${left}px`)
        .style('top', `${top}px`)
    })
    .on('mouseout', function () {
      tooltip.style('display', 'none')
      d3.select(this).classed('box', false)
    })

  // Brush for vessels
  const brushVessel = d3.brushY()
    .extent([[-10, 0], [10, _height]])
    .on('end', (event: any) => {
      if (!event.selection) return
      const selected = yVessel.domain().filter(d => {
        const pos = yVessel(d) + yVessel.bandwidth() / 2
        return event.selection[0] <= pos && pos <= event.selection[1]
      })
      store.selectedVesselIDs = selected
    })

  // Brush for x-axis
  const brushX = d3.brushX()
    .extent([[0, _height], [_width, _height + 10]])
    .on('end', (event: any) => {
      if (!event.selection) return
      const [start, end] = event.selection.map(x.invert)
      store.dateInterval = [d3.timeFormat('%Y-%m-%d')(start), d3.timeFormat('%Y-%m-%d')(end)]
    })

  svg.append('g')
    .attr('class', 'brushVessel')
    .call(brushVessel)

  svg.append('g')
    .attr('class', 'brushX')
    .call(brushX)
}

watch([transportMovements, focusVesselID, selectedVesselIDs, selectedLocationIDs, selectedCommodityIDs, dateInterval], ([newTransportMovements, newFocusVesselID, newSelectedVesselIDs, newSelectedLocationIDs, newSelectedCommodityIDs, newDateInterval]) => {
  if (newTransportMovements.length > 0
    && newSelectedVesselIDs.length > 0
    && newSelectedLocationIDs.length > 0
    && newSelectedCommodityIDs.length > 0
    && d3.timeParse('%Y-%m-%d')('2035-2-1') <= d3.timeParse('%Y-%m-%d')(newDateInterval[0])
    && d3.timeParse('%Y-%m-%d')(newDateInterval[1]) <= d3.timeParse('%Y-%m-%d')('2035-12-31')
  )
    renderChart(harborMovements.value, commodityDistributions.value, newFocusVesselID, newSelectedVesselIDs, newSelectedLocationIDs, newSelectedCommodityIDs, newDateInterval)
}, { immediate: true })
</script>

<template>
  <div id="chart1" />
</template>
