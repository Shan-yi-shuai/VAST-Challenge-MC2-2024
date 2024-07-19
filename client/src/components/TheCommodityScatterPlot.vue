<script setup lang='ts'>
import { storeToRefs } from 'pinia'
import * as d3 from 'd3'
import { onMounted, watch } from 'vue'
import { useStore } from '../stores/store'

const {
  width,
  height,
} = defineProps({
  width: { default: 1500 },
  height: { default: 900 },
})

const store = useStore()
const { commodityDistributions } = storeToRefs(store)

function drawScatterPlot(commodityDistributions) {
  const margin = { top: 5, right: 5, bottom: 5, left: 5 }
  // 设置 SVG 画布
  const _width = width - margin.left - margin.right
  const _height = height - margin.top - margin.bottom
  const svg = d3.select('#scatter-plot')
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // 处理数据，将日期转换为 Date 对象
  commodityDistributions.forEach(d => {
    d.date = new Date(d.date)
  })

  // 设置 X 轴和 Y 轴的刻度
  const x = d3.scaleTime()
    .domain(d3.extent(commodityDistributions, d => d.date))
    .range([0, _width])

  const y = d3.scalePoint()
    .domain([...new Set(commodityDistributions.map(d => d.location_id))])
    .range([_height, 0])

  // 添加 X 轴
  svg.append('g')
    .attr('transform', `translate(0, ${_height})`)
    .call(d3.axisBottom(x))

  // 添加 Y 轴
  svg.append('g')
    .call(d3.axisLeft(y))

  // 设置颜色比例尺
  const color = d3.scaleOrdinal(d3.schemeCategory10)

  // 绘制散点
  svg.selectAll('circle')
    .data(commodityDistributions)
    .enter().append('circle')
    .attr('cx', d => x(d.date))
    .attr('cy', d => y(d.location_id))
    .attr('r', 2)
    .attr('fill', d => color(d.commodity_id))
    .append('title')
    .text(d => `Date: ${d.date.toISOString().split('T')[0]}, Location: ${d.location_id}, Commodity: ${d.commodity_id}`)
}

watch([commodityDistributions], ([newCommodityDistributions]) => {
  if (newCommodityDistributions.length > 0)
    drawScatterPlot(JSON.parse(JSON.stringify(newCommodityDistributions)))
}, { immediate: true })
</script>

<template>
  <div id="scatter-plot" />
</template>

<style scoped>
#heatmap {
  font-family: Arial, sans-serif;
}
</style>
