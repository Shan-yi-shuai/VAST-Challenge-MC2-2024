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
const { transportMovements, selectedVesselIDs, selectedLocationIDs, dateInterval, focusVesselID, locationColor, locationID2Name, vesselID2Name } = storeToRefs(store)

function getRegionAverageDuration(transportMovements: any, regionIDs: any, selectedVesselIDs: any): any {
  const regionAverageDuration: any = {}
  regionIDs.forEach((regionID: string) => {
    const regionMovements = transportMovements.filter((d: TransportMovement) => d.location_id === regionID && selectedVesselIDs.includes(d.vessel_id))
    const regionDuration = regionMovements.reduce((acc: number, cur: TransportMovement) => acc + (d3.timeParse('%Y-%m-%dT%H:%M:%S')(cur.end_time).getTime() - d3.timeParse('%Y-%m-%dT%H:%M:%S')(cur.start_time).getTime()), 0)
    regionAverageDuration[regionID] = (regionDuration / regionMovements.length) / (1000 * 60 * 60 * 24)
  })
  return regionAverageDuration
}

function formatDuration(duration: number): string {
  const d = duration * (1000 * 60 * 60 * 24)
  const millisecondsInOneHour = 1000 * 60 * 60
  const millisecondsInOneDay = millisecondsInOneHour * 24

  const days = Math.floor(d / millisecondsInOneDay)
  const hours = Math.floor((d % millisecondsInOneDay) / millisecondsInOneHour)
  const minutes = Math.floor((d % millisecondsInOneHour) / (1000 * 60))

  return `${days} day(s) ${hours} hour(s) ${minutes} minute(s)`
}

function renderChart(originalTransportMovements: any, focusVesselID: any, selectedVesselIDs: any, selectedLocationIDs: any, dateInterval: any): void {
  const regionIDs = [
    'Cod Table',
    'Wrasse Beds',
    'Tuna Shelf',
    'Ghoti Preserve',
    'Nemo Reef',
    'Don Limpet Preserve',
  ]
  const filteredRegionIDs = regionIDs.filter((d: string) => selectedLocationIDs.includes(d))
  const transportMovements = originalTransportMovements.filter((d: any) => selectedVesselIDs.includes(d.vessel_id)).filter((d: any) => selectedLocationIDs.includes(d.location_id)).filter((d: any) => d3.timeParse('%Y-%m-%d')(dateInterval[0]) <= d3.timeParse('%Y-%m-%dT%H:%M:%S')(d.start_time) && d3.timeParse('%Y-%m-%dT%H:%M:%S')(d.start_time) <= d3.timeParse('%Y-%m-%d')(dateInterval[1]))
  const transportMovementsCopy = JSON.parse(JSON.stringify(transportMovements))

  const aggregateRegionAverageDuration = getRegionAverageDuration(transportMovementsCopy, filteredRegionIDs, selectedVesselIDs)
  const focusRegionAverageDuration = getRegionAverageDuration(transportMovementsCopy, filteredRegionIDs, [focusVesselID])
  const combinedData: any = {}
  filteredRegionIDs.forEach((regionID: string) => {
    combinedData[regionID] = [aggregateRegionAverageDuration[regionID], focusRegionAverageDuration[regionID]]
  })

  const margin = { top: 10, right: 10, bottom: 20, left: 30 }
  const _width = width - margin.left - margin.right
  const _height = height - margin.top - margin.bottom

  d3.select('#bar').selectAll('*').remove()
  const svg = d3.select('#bar')
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // Define pattern for hatching
  svg.append('defs')
    .append('pattern')
    .attr('id', 'hatch')
    .attr('patternUnits', 'userSpaceOnUse')
    .attr('width', 4)
    .attr('height', 4)
    .append('path')
    .attr('d', `M-1,1 l2,-2
                M0,4 l4,-4
                M3,5 l2,-2`)
    .attr('stroke', '#000')
    .attr('stroke-width', 1)

  const x0 = d3.scaleBand()
    .domain(filteredRegionIDs)
    .rangeRound([0, _width])
    .paddingInner(0.1)

  const x1 = d3.scaleBand()
    .domain(['aggregation', 'focus'])
    .rangeRound([0, x0.bandwidth()])
    .padding(0.05)

  const y = d3.scaleLinear()
    .domain([0, d3.max(Object.values(combinedData).flat())])
    .nice()
    .rangeRound([_height, 0])

  // Tooltip div
  const tooltip = d3.select('body')
    .append('div')
    .style('position', 'absolute')
    .style('background', '#fff')
    .style('border', '1px solid #000')
    .style('padding', '5px')
    .style('display', 'none')
    .style('pointer-events', 'none')

  svg.append('g')
    .selectAll('g')
    .data(filteredRegionIDs)
    .enter().append('g')
    .attr('transform', d => `translate(${x0(d)},0)`)
    .selectAll('rect')
    .data(d => ['aggregation', 'focus'].map(key => ({ key, value: [combinedData[d][key === 'aggregation' ? 0 : 1], d] })))
    .enter().append('rect')
    .attr('x', d => x1(d.key))
    .attr('y', d => y(d.value[0]))
    .attr('width', x1.bandwidth())
    .attr('height', d => _height - y(d.value[0]))
    .attr('fill', d => d.key === 'aggregation' ? 'url(#hatch)' : locationColor.value(d.value[1]))
    .on('mouseover', function (event, d: TransportMovement) {
      tooltip.style('display', 'block')
        .html(`${d.key}<br>Location: ${locationID2Name.value[d.value[1]]}<br>Average Duration: ${formatDuration(d.value[0])}`)
      d3.select(this).classed('box', true)
      d3.select(this).style('stroke', 'black')
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
      d3.select(this).style('stroke', 'none')
    })

  svg.append('g')
    .attr('class', 'axis')
    .attr('transform', `translate(0,${_height})`)
    .call(d3.axisBottom(x0))
    .attr('font-size', 8)
    .selectAll('text')
    .text(d => d in locationID2Name.value ? locationID2Name.value[d] : d)

  svg.append('g')
    .attr('class', 'axis')
    .call(d3.axisLeft(y).ticks(null, 's'))

  const legend = svg.append('g')
    .attr('transform', `translate(${_width - 20}, ${margin.top})`)

  legend.append('rect')
    .attr('x', 0)
    .attr('y', 0)
    .attr('width', 18)
    .attr('height', 18)
    .attr('fill', 'url(#hatch)')

  legend.append('text')
    .attr('x', -5)
    .attr('y', 9)
    .attr('dy', '0.2em')
    .attr('text-anchor', 'end')
    .text('Aggregation')
    .attr('font-size', 8)

  // legend.append('rect')
  //   .attr('x', 0)
  //   .attr('y', 24)
  //   .attr('width', 18)
  //   .attr('height', 18)
  //   .attr('fill', locationColor.value('SomeLocation'))

  // legend.append('text')
  //   .attr('x', 24)
  //   .attr('y', 33)
  //   .attr('dy', '0.35em')
  //   .text('Focus')
}

watch([transportMovements, focusVesselID, selectedVesselIDs, selectedLocationIDs, dateInterval], ([newTransportMovements, newFocusVesselID, newSelectedVesselIDs, newSelectedLocationIDs, newDateInterval]) => {
  if (newTransportMovements.length > 0
    && newSelectedVesselIDs.length > 0
    && newSelectedLocationIDs.length > 0
    && d3.timeParse('%Y-%m-%d')('2035-2-1') <= d3.timeParse('%Y-%m-%d')(newDateInterval[0])
    && d3.timeParse('%Y-%m-%d')(newDateInterval[1]) <= d3.timeParse('%Y-%m-%d')('2035-12-31')
  )
    renderChart(transportMovements.value, newFocusVesselID, newSelectedVesselIDs, newSelectedLocationIDs, newDateInterval)
}, { immediate: true })
</script>

<template>
  <div id="bar" />
</template>