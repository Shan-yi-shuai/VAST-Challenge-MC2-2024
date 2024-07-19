<script setup lang='ts'>
import { storeToRefs } from 'pinia'
import * as d3 from 'd3'
import { watch } from 'vue'
import { useStore } from '../stores/store'
import { on } from 'events';

interface TransportMovement {
  start_time: string | Date
  end_time: string | Date
  vessel_id: string
  location_id: string
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
const { transportMovements, aggregateVesselMovements, focusVesselID, selectedVesselIDs, selectedLocationIDs, dateInterval, vesselTypeColor, locationColor, vesselID2Name, locationID2Name } = storeToRefs(store)

function renderChart(transportMovements: any, aggregateVesselMovements: any, focusVesselID: any, selectedVesselIDs: any, selectedLocationIDs: any, dateInterval: any): void {
  const transportMovementsCopy = JSON.parse(JSON.stringify(transportMovements))
  const aggregateVesselMovementsCopy = JSON.parse(JSON.stringify(aggregateVesselMovements))
  const focusVesselMovementsCopy = transportMovementsCopy.filter((d: any) => d.vessel_id === focusVesselID && d3.timeParse('%Y-%m-%d')(dateInterval[0]) <= d3.timeParse('%Y-%m-%dT%H:%M:%S')(d.start_time) && d3.timeParse('%Y-%m-%dT%H:%M:%S')(d.start_time) <= d3.timeParse('%Y-%m-%d')(dateInterval[1]))
  const combinedData = [...aggregateVesselMovementsCopy, ...focusVesselMovementsCopy]

  const parseDate1 = d3.timeParse('%Y-%m-%dT%H:%M:%S')
  combinedData.forEach((d: any) => {
    d.start_time = parseDate1(d.start_time)
    d.end_time = parseDate1(d.end_time)
  })

  const margin = { top: 10, right: 10, bottom: 10, left: 20 }
  const _width = width - margin.left - margin.right
  const _height = height - margin.top - margin.bottom

  d3.select('#chart3').selectAll('*').remove()
  const svg = d3.select('#chart3')
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // 设置时间轴范围
  const x = d3.scaleTime()
    .domain(dateInterval.map((d: string) => d3.timeParse('%Y-%m-%d')(d)) as [Date, Date])
    .range([0, _width-40])

  const yVessel = d3.scaleBand()
    .domain(combinedData.map((d: TransportMovement) => d.vessel_id))
    .range([0, _height - 10])
    .padding(0.1)

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
      const vessel = combinedData.find(v => v.vessel_id === d)
      if (vessel && d !== 'aggregation')
        return vesselTypeColor.value(vessel.vessel_type)
      return 'black'
    })
    .text(d => d in vesselID2Name.value ? vesselID2Name.value[d] : d)
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
    .data(combinedData)
    .enter().append('rect')
    .attr('class', 'bar vessel')
    .attr('x', (d: TransportMovement) => x(d.start_time as Date))
    .attr('y', (d: TransportMovement) => yVessel(d.vessel_id) as number)
    .attr('width', (d: TransportMovement) => x(d.end_time as Date) - x(d.start_time as Date))
    .attr('height', yVessel.bandwidth())
    .attr('fill', (d: any) => locationColor.value(d.location_id))
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

  // Brush for x-axis
  const brushX = d3.brushX()
    .extent([[0, 3 * _height / 4], [_width, 3 * _height / 4 + 10]])
    .on('end', (event: any) => {
      if (!event.selection) return
      const [start, end] = event.selection.map(x.invert)
      store.dateInterval = [d3.timeFormat('%Y-%m-%d')(start), d3.timeFormat('%Y-%m-%d')(end)]
    })

  svg.append('g')
    .attr('class', 'brushX')
    .call(brushX)
}

watch([transportMovements, aggregateVesselMovements, focusVesselID, selectedVesselIDs, selectedLocationIDs, dateInterval], ([newTransportMovements, newAggregateVesselMovements, newFocusVesselID, newSelectedVesselIDs, newSelectedLocationIDs, newDateInterval]) => {
  if (newTransportMovements.length > 0
    && newAggregateVesselMovements.length > 0
    && newSelectedVesselIDs.length > 0
    && newSelectedLocationIDs.length > 0
    && d3.timeParse('%Y-%m-%d')('2035-2-1') <= d3.timeParse('%Y-%m-%d')(newDateInterval[0])
    && d3.timeParse('%Y-%m-%d')(newDateInterval[1]) <= d3.timeParse('%Y-%m-%d')('2035-12-31')
  )
    renderChart(newTransportMovements, newAggregateVesselMovements, newFocusVesselID, newSelectedVesselIDs, newSelectedLocationIDs, newDateInterval)

}, { immediate: true })

watch([selectedLocationIDs, selectedVesselIDs, dateInterval], ([newSelectedLocationIDs, newSelectedVesselIDs, newDateInterval]) => {
  if (newSelectedLocationIDs.length > 0
    && newSelectedVesselIDs.length > 0
    && d3.timeParse('%Y-%m-%d')('2035-2-1') <= d3.timeParse('%Y-%m-%d')(newDateInterval[0])
    && d3.timeParse('%Y-%m-%d')(newDateInterval[1]) <= d3.timeParse('%Y-%m-%d')('2035-12-31')
  )
    store.getAggregatedVesselMovements()
}, { immediate: true })
</script>

<template>
  <div id="chart3" />
</template>
