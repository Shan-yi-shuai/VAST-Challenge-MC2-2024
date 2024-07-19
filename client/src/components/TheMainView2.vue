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
  start_time: string | Date
  end_time: string | Date
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
const { transportMovements, commodityDistributions, selectedVesselIDs, selectedLocationIDs, selectedCommodityIDs, dateInterval, vesselID2Vessel, focusVesselID, vesselTypeColor, locationColor, vesselID2Name, locationID2Name } = storeToRefs(store)

function renderChart(originalTransportMovements: any, originalCommodityDistributions: any, focusVesselID: any, selectedVesselIDs: any, selectedLocationIDs: any, selectedCommodityIDs: any, dateInterval: any): void {
  const transportMovements = originalTransportMovements.filter((d: any) => selectedVesselIDs.includes(d.vessel_id)).filter((d: any) => selectedLocationIDs.includes(d.location_id)).filter((d: any) => d3.timeParse('%Y-%m-%d')(dateInterval[0]) <= d3.timeParse('%Y-%m-%dT%H:%M:%S')(d.start_time) && d3.timeParse('%Y-%m-%dT%H:%M:%S')(d.start_time) <= d3.timeParse('%Y-%m-%d')(dateInterval[1]))
  const transportMovementsCopy = JSON.parse(JSON.stringify(transportMovements))

  const parseDate1 = d3.timeParse('%Y-%m-%dT%H:%M:%S')

  transportMovementsCopy.forEach((d: any) => {
    d.start_time = parseDate1(d.start_time)
    d.end_time = parseDate1(d.end_time)
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

  d3.select('#chart2').selectAll('*').remove()
  const svg = d3.select('#chart2')
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

  // // Combine multiple color schemes to get enough colors
  // const colorRange = d3.schemeSet3.concat(d3.schemeTableau10, d3.schemePastel1)
  // const color = d3.scaleOrdinal(colorRange).domain(locationIDs.value)

  // // 创建一个颜色比例尺用于vessel_type
  // const typeColor = d3.scaleOrdinal(d3.schemeCategory10)
  //   .domain(vesselTypes.value)

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
    .attr('x', (d: TransportMovement) => x(d.start_time as Date))
    .attr('y', (d: TransportMovement) => yVessel(d.vessel_id) as number)
    .attr('width', (d: TransportMovement) => x(d.end_time as Date) - x(d.start_time as Date)) // 占至少一天的长度
    .attr('height', yVessel.bandwidth())
    .attr('fill', (d: VesselMovement) => locationColor.value(d.location_id))
    .attr('stroke', 'none')
    .on('mouseover', function (event, d: TransportMovement) {
      tooltip.style('display', 'block')
        .html(`Vessel: ${vesselID2Name.value[d.vessel_id]}<br>Start time: ${d3.timeFormat('%Y-%m-%d')(d.start_time as Date)}<br>End time: ${d3.timeFormat('%Y-%m-%d')(d.end_time as Date)}<br>Location: ${locationID2Name.value[d.location_id]}`)
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

  // 添加图例
  // const legend = svg.selectAll('.legend')
  //   .data(color.domain())
  //   .enter().append('g')
  //   .attr('class', 'legend')
  //   .attr('transform', (d: any, i: number) => `translate(0,${i * 10})`)
  //   .on('click', function (event, d: string) {
  //     event.stopPropagation()
  //     const isActive = d3.select(this).classed('active')
  //     d3.selectAll('.legend').classed('active', false).select('rect').style('stroke', 'none')
  //     d3.selectAll('.bar').style('fill', (d: any) => color(d.location_id))

  //     if (!isActive) {
  //       d3.select(this).classed('active', true).select('rect').style('stroke', 'black')
  //       svg.selectAll('.bar')
  //         .filter((barData: any) => barData.location_id === d)
  //         .style('fill', 'black')
  //     }
  //   })

  // legend.append('rect')
  //   .attr('x', _width)
  //   .attr('width', 9)
  //   .attr('height', 9)
  //   .style('fill', color)

  // legend.append('text')
  //   .attr('x', _width - 5)
  //   .attr('y', 4)
  //   .attr('dy', '.35em')
  //   .attr('font-size', 4)
  //   .style('text-anchor', 'end')
  //   .text((d: string) => d)

  // // 添加vessel_type的图例
  // const typeLegend = svg.selectAll('.type-legend')
  //   .data(typeColor.domain())
  //   .enter().append('g')
  //   .attr('class', 'type-legend')
  //   .attr('transform', (d, i) => `translate(0,${(i + color.domain().length) * 10 + 10})`)

  // typeLegend.append('rect')
  //   .attr('x', _width)
  //   .attr('width', 9)
  //   .attr('height', 3)
  //   .style('fill', typeColor)

  // typeLegend.append('text')
  //   .attr('x', _width - 5)
  //   .attr('y', 1)
  //   .attr('dy', '.35em')
  //   .attr('font-size', 4)
  //   .style('text-anchor', 'end')
  //   .text(d => d)

  // 添加透明矩形捕获鼠标点击事件
  // const clickCatcher = svg.append('rect')
  //   .attr('width', _width)
  //   .attr('height', _height)
  //   .attr('fill', 'none')
  //   .style('pointer-events', 'none') // 默认情况下禁用pointer-events

  // svg.on('click', (event: any) => {
  //   clickCatcher.style('pointer-events', 'all') // 启用pointer-events以捕获点击事件

  //   const [xCoord] = d3.pointer(event)
  //   const clickedDate = x.invert(xCoord)
  //   const formattedClickedDate = d3.timeFormat('%Y-%m-%d')(clickedDate)
  //   const startOfDay = d3.timeParse('%Y-%m-%d')(formattedClickedDate)
  //   const endOfDay = d3.timeDay.offset(startOfDay, 1)

  //   const existingRect = svg.select(`.selected-day[x="${x(startOfDay)}"]`)

  //   if (existingRect.empty()) {
  //     svg.selectAll('.selected-day').remove()

  //     svg.append('rect')
  //       .attr('class', 'selected-day')
  //       .attr('x', x(startOfDay))
  //       .attr('y', 0)
  //       .attr('width', x(endOfDay) - x(startOfDay))
  //       .attr('height', height)
  //       .attr('fill', 'none')
  //       .attr('stroke', 'black')
  //       .attr('stroke-width', 1)
  //   }
  //   else {
  //     existingRect.remove()
  //   }

  //   clickCatcher.style('pointer-events', 'none') // 处理完点击事件后禁用pointer-events
  // })

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
    renderChart(transportMovements.value, commodityDistributions.value, newFocusVesselID, newSelectedVesselIDs, newSelectedLocationIDs, newSelectedCommodityIDs, newDateInterval)
}, { immediate: true })
</script>

<template>
  <div id="chart2" />
</template>

<style scoped>
.bar {
  stroke: none;
}

.box {
  stroke: black;
}

.axis text {
  font-size: 10px;
}

.axis path,
.axis line {
  fill: none;
  shape-rendering: crispEdges;
}

.legend rect {
  cursor: pointer;
}

.legend.active rect {
  stroke: black;
}
</style>
