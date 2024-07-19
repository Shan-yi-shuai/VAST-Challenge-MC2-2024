<script setup lang='ts'>
import { storeToRefs } from 'pinia'
import * as d3 from 'd3'
import { onMounted, watch } from 'vue'
import { useStore } from '../stores/store'

interface VesselMovement {
  date: string | Date
  vessel_id: string
  location_id: string
}

const {
  width,
  height,
} = defineProps({
  width: { default: 1500 },
  height: { default: 900 },
})

// acquire pinia store
const store = useStore()
const { vesselMovements, locationCoordinates, geoData, selectedVesselIDs, selectedLocationIDs, dateInterval, locationIDs, locationID2Location } = storeToRefs(store)

// 计算多边形的面积以确定点的顺序
function ringArea(coords: any) {
  let area = 0
  let x0 = coords[0][0]
  let y0 = coords[0][1]
  for (let i = 1; i < coords.length; i++) {
    const x1 = coords[i][0]
    const y1 = coords[i][1]
    area += x1 * y0 - x0 * y1
    x0 = x1
    y0 = y1
  }
  return area / 2
}

// 确保多边形的点按照逆时针顺序排列
function correctPolygonOrder(polygon: any) {
  if (ringArea(polygon[0]) < 0)
    polygon[0].reverse()
  for (let i = 1; i < polygon.length; i++) {
    if (ringArea(polygon[i]) > 0)
      polygon[i].reverse()
  }
}

// 确保多边形和多多边形的点顺序正确
function correctGeoJsonOrder(geoJsonData: any) {
  geoJsonData.features.forEach((feature: any) => {
    if (feature.geometry.type === 'Polygon') {
      correctPolygonOrder(feature.geometry.coordinates)
    }
    else if (feature.geometry.type === 'MultiPolygon') {
      feature.geometry.coordinates.forEach((polygon: any) => {
        correctPolygonOrder(polygon)
      })
    }
  })
}

function processData(data) {
  const lineData: any[] = []

  for (const key in data) {
    const movements = data[key]
    for (let i = 0; i < movements.length - 1; i++) {
      const from = movements[i][1]
      const to = movements[i + 1][1]
      const line = lineData.find(d => (d[0] === from && d[1] === to) || (d[0] === to && d[1] === from))
      if (line)
        line[2]++
      else
        lineData.push([from, to, 1])
    }
  }

  return lineData
}

function getCoordinatesByLocationID(locationID: string) {
  const locationName = locationID2Location.value[locationID].Name
  return locationCoordinates.value.features.find((feature: any) => feature.properties.Name === locationName).geometry.coordinates
}

function getVesselMovementSequences(vesselMovements: any[]) {
  const vesselMovementSequences: MovementSequence = {}

  vesselMovements.forEach((record) => {
    const { vessel_id, start_time, location_id } = record

    if (!vesselMovementSequences[vessel_id])
      vesselMovementSequences[vessel_id] = []
    vesselMovementSequences[vessel_id].push([start_time, location_id])
  })

  Object.keys(vesselMovementSequences).forEach((vesselId) => {
    vesselMovementSequences[vesselId].sort((a, b) => new Date(a[0]).getTime() - new Date(b[0]).getTime())
  })

  return vesselMovementSequences
}

function drawMovements(geoJsonData: any, locationCoordinates: any, vesselMovements: VesselMovement[], selectedVesselIDs: any[], selectedLocationIDs: any[], dateInterval: any[]) {
  d3.select('#map').selectAll('*').remove()
  const svg = d3.select('#map').append('svg')
    .attr('width', width)
    .attr('height', height)

  const g = svg.append('g')
  correctGeoJsonOrder(geoJsonData)
  const bounds = d3.geoBounds(geoJsonData)
  const center = [(bounds[0][0] + bounds[1][0]) / 2, (bounds[0][1] + bounds[1][1]) / 2]
  const distance = Math.max(bounds[1][0] - bounds[0][0], bounds[1][1] - bounds[0][1])
  const scale = (Math.max(width, height) / distance) * 40 // Adjust scale factor as needed

  const projection = d3.geoMercator()
    .scale(scale)
    .center(center)
    .translate([width / 2, height / 2])

  const path = d3.geoPath().projection(projection)

  const tooltip = d3.select('body')
    .append('div')
    .style('position', 'absolute')
    .style('background', '#fff')
    .style('border', '1px solid #000')
    .style('padding', '1px')
    .style('display', 'none')
    .style('pointer-events', 'none')

  // 绘制GeoJSON特征
  g.selectAll('path')
    .data(geoJsonData.features)
    .enter().append('path')
    .attr('d', path)
    .attr('fill', (d: any) => {
      // TODO: change the color of different regions
      const type = d.properties.type
      if (type === 'Entity.Location.Region') {
        if (['Cod Table', 'Wrasse Beds', 'Tuna Shelf'].includes(d.properties.Name))
          return 'lightgreen'
        if (['Ghoti Preserve', 'Nemo Reef', 'Don Limpet Preserve'].includes(d.properties.Name))
          return 'lightcoral'
        return 'lightblue'
      }
      else if (type === 'Entity.Location.City') {
        return 'gray'
      }
      else {
        return 'lightgray'
      }
    })
    .attr('stroke', 'black')
    .attr('stroke-width', 0.5)
    .on('mouseover', function (event, d: any) {
      const fishSpeciesPresent = d.properties.fish_species_present
      let htmlStr = `Location: ${d.properties.Name}<br>Type: ${d.properties.type}<br>Activities: ${d.properties.Activities.join(', ')}<br>Kind: ${d.properties['*Kind']}`
      if (fishSpeciesPresent)
        htmlStr += `<br>Fish Species Present: ${fishSpeciesPresent.join(',<br>')}`
      tooltip.style('display', 'block')
        .html(htmlStr)
      d3.select(this).classed('box', true)
      d3.select(this).attr('stroke-width', 2)
    })
    .on('mousemove', (event, d) => {
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
      d3.select(this).attr('stroke-width', 0.5)
    })

  const filterVesselMovements = vesselMovements.filter((d: any) => {
    return selectedVesselIDs.includes(d.vessel_id)
      && selectedLocationIDs.includes(d.location_id)
      && d3.timeParse('%Y-%m-%d')(dateInterval[0]) <= d3.timeParse('%Y-%m-%dT%H:%M:%S')(d.start_time)
      && d3.timeParse('%Y-%m-%dT%H:%M:%S')(d.start_time) <= d3.timeParse('%Y-%m-%d')(dateInterval[1])
  })

  const data = getVesselMovementSequences(filterVesselMovements)
  const lineData = processData(data)

  // Todo
  const filteredLineData = lineData.filter((d: any) => d[2] >= selectedVesselIDs.length / selectedLocationIDs.length)

  // 创建颜色比例尺
  const opacityScale = d3.scaleSequential()
    .domain([d3.min(lineData, (d: any) => d[2]), d3.max(lineData, (d: any) => d[2])])
    .range([0.1, 1])

  svg.append('g')
    .selectAll('line')
    .data(filteredLineData)
    .enter().append('line')
    .attr('x1', (d) => projection(getCoordinatesByLocationID(d[0]))[0])
    .attr('y1', (d) => projection(getCoordinatesByLocationID(d[0]))[1])
    .attr('x2', (d) => projection(getCoordinatesByLocationID(d[1]))[0])
    .attr('y2', (d) => projection(getCoordinatesByLocationID(d[1]))[1])
    .attr('stroke', 'black')
    .style('stroke-width', 1)
    .attr('stroke-opacity', (d: any) => opacityScale(d[2]))
    .on('mouseover', function (event, d: any) {
      tooltip.style('display', 'block')
        .html(`${d[0]}-${d[1]}-${d[2]}`)
      d3.select(this).classed('box', true)
      d3.select(this).attr('stroke-opacity', 1).style('stroke-width', 2)
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
        left = svgBounds.right - tooltipWidth - 10
      if (top + tooltipHeight > svgBounds.bottom)
        top = svgBounds.bottom - tooltipHeight - 10

      tooltip.style('left', `${left}px`)
        .style('top', `${top}px`)
    })
    .on('mouseout', function () {
      tooltip.style('display', 'none')
      d3.select(this).classed('box', false)
      d3.select(this).attr('stroke-opacity', (d: any) => opacityScale(d[2])).style('stroke-width', 1)
    })
}

watch([vesselMovements, selectedVesselIDs, selectedLocationIDs, dateInterval], ([newVesselMovements, newSelectedVesselIDs, newSelectedLocationIDs, newDateInterval]) => {
  if (newVesselMovements.length > 0
    && newSelectedVesselIDs.length > 0
    && newSelectedLocationIDs.length > 0
    && d3.timeParse('%Y-%m-%d')('2035-2-1') <= d3.timeParse('%Y-%m-%d')(newDateInterval[0])
    && d3.timeParse('%Y-%m-%d')(newDateInterval[1]) <= d3.timeParse('%Y-%m-%d')('2035-12-31')
  )
    drawMovements(geoData.value, locationCoordinates.value, newVesselMovements, newSelectedVesselIDs, newSelectedLocationIDs, newDateInterval)
}, { immediate: true })
</script>

<template>
  <div>
    <div id="map" />
  </div>
</template>

<style scoped>
body {
  font-family: Arial, sans-serif
}

.tooltip {
  position: absolute;
  text-align: center;
  width: auto;
  height: auto;
  padding: 5px;
  font: 12px sans-serif;
  background: lightsteelblue;
  border: 0px;
  border-radius: 8px;
  pointer-events: none;
}

#map {
  margin-bottom: 20px
}
</style>
