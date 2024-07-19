<script setup lang='ts'>
import { storeToRefs } from 'pinia'
import * as d3 from 'd3'
import { onMounted, watch } from 'vue'
import { useStore } from '../stores/store'

interface CommodityDistribution {
  date: string | Date
  commodity_id: string
  location_id: string
  document_id: string
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
const { commodityDistributions, locationCoordinates, geoData, dateInterval, commoditys, commodityFishingLocations } = storeToRefs(store)

const dateRangeValue = ref(364)
const currentDate = ref('2035-12-31')

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

function drawDistributions(geoJsonData: any, commodityDistributions: CommodityDistribution[], dateInterval: { start: string; end: string }, commoditys: string[]) {
  const svg = d3.select('#commodityMap').append('svg')
    .attr('width', width)
    .attr('height', height)

  const g = svg.append('g')

  const projection = d3.geoMercator()
    .scale(4800)
    .center([-165, 39.4])
    .translate([width / 2, height / 2])

  const path = d3.geoPath().projection(projection)
  correctGeoJsonOrder(geoJsonData)

  // 绘制GeoJSON特征
  g.selectAll('path')
    .data(geoJsonData.features)
    .enter().append('path')
    .attr('d', path)
    .attr('fill', (d: any) => {
      // TODO: change the color of different regions
      const type = d.properties.type
      if (type === 'Entity.Location.Region')
        return 'lightblue'
      else if (type === 'Entity.Location.City')
        return 'lightgreen'
      else
        return 'white'
    })
    .attr('stroke', 'black')
    .attr('stroke-width', 0.5)

  // 显示区域名称
  // g.selectAll('text')
  //   .data(geoJsonData.features)
  //   .enter().append('text')
  //   .attr('x', (d: any) => {
  //     const centroid = path.centroid(d)
  //     return centroid[0]
  //   })
  //   .attr('y', (d: any) => {
  //     const centroid = path.centroid(d)
  //     return centroid[1]
  //   })
  //   .text((d: any) => d.properties.Name)
  //   .attr('font-size', '10px')
  //   .attr('fill', 'black')

  const tooltip = d3.select('body').append('div')
    .attr('class', 'tooltip')
    .style('opacity', 0)

  const minDate = new Date('2035-1-1')
  const maxDate = new Date('2035-12-31')

  // 创建颜色比例尺
  const colorScale = d3.scaleSequential(d3.interpolateGreens)
    .domain([minDate, maxDate])

  const filteredData = commodityDistributions.filter(d => (new Date(d.date) <= new Date(dateInterval.end) && new Date(d.date) >= new Date(dateInterval.start) && commoditys.includes(d.commodity_id)))
  // const filteredData = vessel_movements
  g.selectAll('.vessel')
    .data(filteredData)
    .enter().append('circle')
    .attr('class', 'vessel')
    .attr('cx', (d: CommodityDistribution) => projection(locationCoordinates.value[d.location_id])[0])
    .attr('cy', (d: CommodityDistribution) => projection(locationCoordinates.value[d.location_id])[1])
    .attr('r', 2)
    .attr('fill', (d: CommodityDistribution) => colorScale(new Date(d.date)))
    .on('mouseover', (event: MouseEvent, d: CommodityDistribution) => {
      tooltip.transition()
        .duration(200)
        .style('opacity', 0.9)
      tooltip.html(`Commodity: ${d.commodity_id}<br/>Location: ${d.location_id}`)
        .style('left', `${event.pageX + 5}px`)
        .style('top', `${event.pageY - 28}px`)
    })
    .on('mouseout', (_: CommodityDistribution) => {
      tooltip.transition()
        .duration(500)
        .style('opacity', 0)
    })

  const groupedData = d3.group(filteredData, (d: CommodityDistribution) => d.commodity_id)
  const pathCounts = new Map<string, number>()
  groupedData.forEach((distributions: CommodityDistribution[], commodity_id: string) => {
    // 计算路径出现次数
    for (let i = 0; i < distributions.length; i++) {
      for (const location_id of commodityFishingLocations.value[commodity_id]) {
        const key = `${distributions[i].location_id}-${location_id}`
        if (distributions[i].location_id === location_id)
          console.log(location_id)
        pathCounts.set(key, (pathCounts.get(key) || 0) + 1)
      }
    }
  })

  const maxCount = Math.max(...pathCounts.values())
  const minCount = Math.min(...pathCounts.values())

  // 创建宽度比例尺，使用对数比例尺
  const widthScale = d3.scaleLog()
    .domain([minCount, maxCount])
    .range([0, 5])

  // 添加箭头标记
  // g.append('defs').append('marker')
  //   .attr('id', 'arrow')
  //   .attr('viewBox', '0 0 10 10')
  //   .attr('refX', 5)
  //   .attr('refY', 5)
  //   .attr('markerWidth', 6)
  //   .attr('markerHeight', 6)
  //   .attr('orient', 'auto-start-reverse')
  //   .append('path')
  //   .attr('d', 'M 0 0 L 10 5 L 0 10 z')
  //   .attr('fill', 'black')

  const usedKeys = new Set<string>()
  groupedData.forEach((distributions: CommodityDistribution[], commodity_id: string) => {
    for (let i = 0; i < distributions.length; i++) {
      for (const location_id of commodityFishingLocations.value[commodity_id]) {
        const key = `${distributions[i].location_id}-${location_id}`
        const coords1 = locationCoordinates.value[distributions[i].location_id]
        const coords2 = locationCoordinates.value[location_id]
        if (coords1 && coords2 && !usedKeys.has(key)) {
          const count = pathCounts.get(key) || 1
          usedKeys.add(key)
          g.append('line')
            .attr('class', 'vessel')
            .attr('x1', projection(coords1)[0])
            .attr('y1', projection(coords1)[1])
            .attr('x2', projection(coords2)[0])
            .attr('y2', projection(coords2)[1])
            .attr('stroke', 'green')
            .attr('stroke-width', widthScale(count))
            .attr('stroke-opacity', 0.5)
            // .attr('marker-end', 'url(#arrow)')
        }
      }
    }
  })
}

function formatDate(dayOfYear: number) {
  const date = new Date(2035, 0) // Starting from January 1, 2035
  date.setDate(date.getDate() + dayOfYear)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0') // Months are zero-based
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

watch([commodityDistributions, dateInterval, commoditys], ([newCommodityDistributions, newDateInterval, newCommoditys]) => {
  if (newCommodityDistributions.length > 0 && newCommoditys.length > 0)
    drawDistributions(geoData.value, newCommodityDistributions, newDateInterval, newCommoditys)
}, { immediate: true })
</script>

<template>
  <div>
    <div id="commodityMap" />
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
