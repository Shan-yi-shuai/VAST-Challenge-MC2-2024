<script setup lang='ts'>
import { storeToRefs } from 'pinia'
import * as d3 from 'd3'
import { watch } from 'vue'
import { useStore } from '../stores/store'
import { on } from 'events';

const {
  width,
  height,
} = defineProps({
  width: { default: 1500, type: Number },
  height: { default: 900, type: Number },
})

// acquire pinia store
const store = useStore()
const { commodityDistributions, vesselMovements, selectedLocationIDs, selectedCommodityIDs, dateInterval, commodityIDs } = storeToRefs(store)
function transformData(data: any): any {
  const result = []

  data.forEach(item => {
    const existing = result.find(
      res => (res.date === item.date && res.commodity_id === item.commodity_id)
    )

    if (existing) {
      existing.locations.push(item.location_id)
    }
    else {
      result.push({
        date: item.date,
        commodity_id: item.commodity_id,
        locations: [item.location_id],
      })
    }
  })

  return result
}

function renderChart(commodityDistributions: any, selectedLocationIDs: any, selectedCommodityIDs: any, dateInterval: any): void {
  const filteredCommodityDistributions = commodityDistributions.filter((d: any) => selectedLocationIDs.includes(d.location_id)).filter((d: any) => selectedCommodityIDs.includes(d.commodity_id)).filter((d: any) => d3.timeParse('%Y-%m-%d')(dateInterval[0]) <= d3.timeParse('%Y-%m-%d')(d.date) && d3.timeParse('%Y-%m-%d')(d.date) <= d3.timeParse('%Y-%m-%d')(dateInterval[1]))
  const filteredMatchResultsCopy = JSON.parse(JSON.stringify(filteredCommodityDistributions))
  // 解析日期
  const parseDate = d3.timeParse('%Y-%m-%d')
  const formatDateToDay = (date: any) => d3.timeFormat('%Y-%m-%d')(date)
  // filteredMatchResultsCopy.forEach((d: any) => d.date = parseDate2(formatDateToDay(parseDate2(d.date))))
  const combinedData = transformData(filteredMatchResultsCopy)
  combinedData.forEach((d: any) => d.date = parseDate(formatDateToDay(parseDate(d.date))))
  const margin = { top: 10, right: 10, bottom: 10, left: 50 }
  const _width = width - margin.left - margin.right
  const _height = height - margin.top - margin.bottom

  d3.select('#commodity2').selectAll('*').remove()
  const svg = d3.select('#commodity2')
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // 设置时间轴范围
  const x = d3.scaleTime()
    .domain(dateInterval.map((d: string) => d3.timeParse('%Y-%m-%d')(d)) as [Date, Date])
    .range([0, _width])

  const yCommodity = d3.scaleBand()
    .domain(combinedData.map((d: any) => d.commodity_id))
    .range([0, _height - 10])
    .padding(0.1)

  // Combine multiple color schemes to get enough colors
  //   const colorRange = d3.schemeSet3.concat(d3.schemeTableau10, d3.schemePastel1)
  const addition = 0
  const colorAggregated = d3.scaleLog()
    .domain([1, d3.max(combinedData, d => d.locations.length) + addition || 10])
    .interpolate(() => d3.interpolateBlues)

  // 绘制时间轴
  svg.append('g')
    .attr('transform', `translate(0,${_height - 10})`)
    .call(d3.axisBottom(x).tickFormat(d3.timeFormat('%Y-%m-%d')))
    .selectAll('text') // 选择所有文本标签
    .style('font-size', '6px') // 设置字体大小为10px

  // 绘制y轴并根据vessel_type设置文本颜色
  const yAxis = svg.append('g')
    .call(d3.axisLeft(yCommodity))

  yAxis.selectAll('text')
    .attr('font-size', 6)
  // .style('fill', d => {
  //   const vessel = sorted_vessel_data.find(v => v.vessel_id === d)
  //   return vessel ? typeColor(vessel.vessel_type) : 'black'
  // })

  const barWidth = x(new Date(d3.timeDay.offset(x.domain()[0], 1))) - x(x.domain()[0])

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
    .attr('x', (d: any) => x(d.date as Date))
    .attr('y', (d: any) => yCommodity(d.commodity_id) as number)
    .attr('width', barWidth) // 占至少一天的长度
    .attr('height', yCommodity.bandwidth())
    .attr('fill', (d: any) => colorAggregated(d.locations.length + addition))
    .attr('stroke', 'none')
    .on('mouseover', function (event, d: any) {
      tooltip.style('display', 'block')
        .html(`Date: ${d3.timeFormat('%Y-%m-%d')(d.date as Date)}<br>Commodity ID: ${d.commodity_id}<br>Location Num:${d.locations.length}`)
      d3.select(this).classed('box', true)
    })
    .on('mousemove', (event) => {
      tooltip.style('left', `${event.pageX + 10}px`)
        .style('top', `${event.pageY + 10}px`)
    })
    .on('mouseout', function () {
      tooltip.style('display', 'none')
      d3.select(this).classed('box', false)
    })

  // 添加图例
  const legend = svg.append('g')
    .attr('class', 'legend')
    .attr('transform', `translate(${_width}, 0)`)

  const legendScale = d3.scaleLinear()
    .domain(colorAggregated.domain())
    .range([0, 200])

  const legendAxis = d3.axisRight(legendScale)
    .ticks(5)

  legend.append('g')
    .selectAll('rect')
    .data(d3.range(1, d3.max(combinedData, d => d.locations.length) + addition || 10, 1))
    .enter().append('rect')
    .attr('y', (d, i) => legendScale(d))
    .attr('width', 20)
    .attr('height', legendScale(1) - legendScale(0))
    .attr('fill', (d) => colorAggregated(d + addition))
}

watch([vesselMovements, commodityDistributions, selectedLocationIDs, selectedCommodityIDs, dateInterval], ([newVesselMovements, newCommodityDistributions, newSelectedLocationIDs, newSelectedCommodityIDs, newDateInterval]) => {
  if (newVesselMovements.length > 0
    && newCommodityDistributions.length > 0
    && newSelectedLocationIDs.length > 0
    && newSelectedCommodityIDs.length > 0
    && d3.timeParse('%Y-%m-%d')('2035-2-1') <= d3.timeParse('%Y-%m-%d')(newDateInterval[0])
    && d3.timeParse('%Y-%m-%d')(newDateInterval[1]) <= d3.timeParse('%Y-%m-%d')('2035-12-31')
  )
    renderChart(newCommodityDistributions, newSelectedLocationIDs, newSelectedCommodityIDs, newDateInterval)
}, { immediate: true })
</script>

<template>
  <div id="commodity2" />
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
