<script setup lang='ts'>
import { storeToRefs } from 'pinia'
import * as d3 from 'd3'
import { watch } from 'vue'
import { useStore } from '../stores/store'

interface MovementSequence {
  [key: string]: [string, string, number][]
}

const {
  width,
  height,
} = defineProps({
  width: { default: 1500 },
  height: { default: 900 },
})

const store = useStore()
const { vesselMovements, selectedVesselIDs, selectedLocationIDs, dateInterval, locationColor, locationID2Name } = storeToRefs(store)

function formatDuration(duration: number): string {
  const millisecondsInOneHour = 1000 * 60 * 60
  const millisecondsInOneDay = millisecondsInOneHour * 24

  const days = Math.floor(duration / millisecondsInOneDay)
  const hours = Math.floor((duration % millisecondsInOneDay) / millisecondsInOneHour)
  const minutes = Math.floor((duration % millisecondsInOneHour) / (1000 * 60))

  return `${days} day(s) ${hours} hour(s) ${minutes} minute(s)`
}

function processData(data) {
  const locations: string[] = []
  const matrix: number[][] = []

  for (const key in data) {
    const movements = data[key]
    for (let i = 0; i < movements.length - 1; i++) {
      const from: string = movements[i][1]
      const to: string = movements[i + 1][1]

      if (!locations.includes(from))
        locations.push(from)
      if (!locations.includes(to))
        locations.push(to)
    }
  }

  locations.sort()

  for (let i = 0; i < locations.length; i++)
    matrix[i] = new Array(locations.length).fill(0)

  for (const key in data) {
    const movements = data[key]
    for (let i = 0; i < movements.length - 1; i++) {
      const from = movements[i][1]
      const to = movements[i + 1][1]
      const fromIndex = locations.indexOf(from)
      const toIndex = locations.indexOf(to)
      matrix[fromIndex][toIndex] += movements[i][2]
    }
  }

  return { locations, matrix }
}

function getVesselMovementSequences(vesselMovements: any[]) {
  const vesselMovementSequences: MovementSequence = {}

  vesselMovements.forEach((record) => {
    const { vessel_id, start_time, location_id, end_time } = record

    if (!vesselMovementSequences[vessel_id])
      vesselMovementSequences[vessel_id] = []
    vesselMovementSequences[vessel_id].push([start_time, location_id, new Date(end_time).getTime() - new Date(start_time).getTime()])
  })

  Object.keys(vesselMovementSequences).forEach((vesselId) => {
    vesselMovementSequences[vesselId].sort((a, b) => new Date(a[0]).getTime() - new Date(b[0]).getTime())
  })

  return vesselMovementSequences
}
function drawChordDiagram(vesselMovements: any[], selectedVesselIDs: any[], selectedLocationIDs: any[], dateInterval: any[]) {
  const filterVesselMovements = vesselMovements.filter((d: any) => {
    return selectedVesselIDs.includes(d.vessel_id)
      && selectedLocationIDs.includes(d.location_id)
      && d3.timeParse('%Y-%m-%d')(dateInterval[0]) <= d3.timeParse('%Y-%m-%dT%H:%M:%S')(d.start_time)
      && d3.timeParse('%Y-%m-%dT%H:%M:%S')(d.start_time) <= d3.timeParse('%Y-%m-%d')(dateInterval[1])
  })
  const data = getVesselMovementSequences(filterVesselMovements)
  const processedData = processData(data)

  // 设置SVG画布
  const innerRadius = Math.min(width, height) * 0.5 - 20
  const outerRadius = innerRadius + 10

  d3.select('#chord').selectAll('*').remove()
  const svg = d3.select('#chord')
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${width / 2},${height / 2})`)

  const chord = d3.chord()
    .padAngle(0.05)
    .sortSubgroups(d3.descending)(processedData.matrix)

  const arc = d3.arc()
    .innerRadius(innerRadius)
    .outerRadius(outerRadius)

  const ribbon = d3.ribbon()
    .radius(innerRadius)

  const tooltip = d3.select('body')
    .append('div')
    .style('position', 'absolute')
    .style('background', '#fff')
    .style('border', '1px solid #000')
    .style('padding', '5px')
    .style('display', 'none')
    .style('pointer-events', 'none')

  svg.append('g')
    .selectAll('path')
    .data(chord.groups)
    .enter().append('path')
    .style('fill', d => locationColor.value(processedData.locations[d.index]))
    .style('stroke', d => d3.rgb(locationColor.value(processedData.locations[d.index])).darker())
    .attr('d', arc)
    .style('stroke-width', 1)
    .on('mouseover', function (event, d: any) {
      tooltip.style('display', 'block')
        .html(`Location: ${locationID2Name.value[processedData.locations[d.index]]}`)
      d3.select(this).classed('box', true)
      d3.select(this).style('stroke-width', 4)
    })
    .on('mousemove', (event) => {
      const [svgX, svgY] = d3.pointer(event)
      const tooltipWidth = tooltip.node().offsetWidth
      const tooltipHeight = tooltip.node().offsetHeight
      const svgBounds = svg.node().getBoundingClientRect()
      let left = svgX + svgBounds.left + 10
      let top = svgY + svgBounds.top + 10

      // Adjust to keep the tooltip within SVG bounds
      // if (left + tooltipWidth > svgBounds.right)
      //   left = svgBounds.right - tooltipWidth - 10
      // if (top + tooltipHeight > svgBounds.bottom)
      //   top = svgBounds.bottom - tooltipHeight - 10

      tooltip.style('left', `${left}px`)
        .style('top', `${top}px`)
    })
    .on('mouseout', function () {
      tooltip.style('display', 'none')
      d3.select(this).classed('box', false)
      d3.select(this).style('stroke-width', 1)
    })

  svg.append('g')
    .attr('fill-opacity', 0.67)
    .selectAll('path')
    .data(chord)
    .enter().append('path')
    .attr('d', ribbon)
    .style('fill', d => locationColor.value(processedData.locations[d.target.index]))
    .style('stroke', d => d3.rgb(locationColor.value(processedData.locations[d.target.index])).darker())
    .style('stroke-width', 1)
    .on('mouseover', function (event, d: any) {
      tooltip.style('display', 'block')
        .html(`From: ${locationID2Name.value[processedData.locations[d.source.index]]} To: ${locationID2Name.value[processedData.locations[d.target.index]]} Duration: ${formatDuration(d.source.value)}<br>From: ${locationID2Name.value[processedData.locations[d.target.index]]} To: ${locationID2Name.value[processedData.locations[d.source.index]]} Duration: ${formatDuration(d.target.value)}`)
      d3.select(this).classed('box', true)
      d3.select(this).style('stroke-width', 4).attr('fill-opacity', 1)
    })
    .on('mousemove', (event) => {
      const [svgX, svgY] = d3.pointer(event)
      const tooltipWidth = tooltip.node().offsetWidth
      const tooltipHeight = tooltip.node().offsetHeight
      const svgBounds = svg.node().getBoundingClientRect()
      let left = svgX + svgBounds.left + 10
      let top = svgY + svgBounds.top + 10

      // Adjust to keep the tooltip within SVG bounds
      // if (left + tooltipWidth > svgBounds.right)
      //   left = svgBounds.right - tooltipWidth - 10
      // if (top + tooltipHeight > svgBounds.bottom)
      //   top = svgBounds.bottom - tooltipHeight - 10

      tooltip.style('left', `${left}px`)
        .style('top', `${top}px`)
    })
    .on('mouseout', function () {
      tooltip.style('display', 'none')
      d3.select(this).classed('box', false)
      d3.select(this).style('stroke-width', 1).attr('fill-opacity', 0.67)
    })

  // svg.append('g')
  //   .selectAll('text')
  //   .data(chord.groups)
  //   .enter().append('text')
  //   .each((d: any) => { d.angle = (d.startAngle + d.endAngle) / 2 })
  //   .attr('dy', '.35em')
  //   .attr('transform', d => `
  //       rotate(${d.angle * 180 / Math.PI - 90})
  //       translate(${outerRadius + 5})
  //       ${d.angle > Math.PI ? 'rotate(180)' : ''}
  //   `)
  //   .attr('text-anchor', d => d.angle > Math.PI ? 'end' : null)
  //   .text(d => processedData.locations[d.index])
  //   .attr('font-size', 4)
}

watch([vesselMovements, selectedVesselIDs, selectedLocationIDs, dateInterval], ([newVesselMovements, newSelectedVesselIDs, newSelectedLocationIDs, newDateInterval]) => {
  if (newVesselMovements.length > 0
    && newSelectedVesselIDs.length > 0
    && newSelectedLocationIDs.length > 0
    && d3.timeParse('%Y-%m-%d')('2035-2-1') <= d3.timeParse('%Y-%m-%d')(newDateInterval[0])
    && d3.timeParse('%Y-%m-%d')(newDateInterval[1]) <= d3.timeParse('%Y-%m-%d')('2035-12-31')
  )
    drawChordDiagram(newVesselMovements, newSelectedVesselIDs, newSelectedLocationIDs, newDateInterval)
}, { immediate: true })
</script>

<template>
  <div id="chord" />
</template>

<style scoped>
#heatmap {
  font-family: Arial, sans-serif;
}
</style>
