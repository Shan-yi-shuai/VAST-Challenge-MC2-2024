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
const { frequencyCommodityVessels } = storeToRefs(store)

function drawHeatmap(heatmapData) {
  const margin = { top: 5, right: 5, bottom: 5, left: 5 }
  // 设置 SVG 画布
  const _width = width - margin.left - margin.right
  const _height = height - margin.top - margin.bottom
  const svg = d3.select('#heatmap3')
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // 设置 X 和 Y 轴的刻度
  const x = d3.scaleBand()
    .range([0, _width])
    .domain([...new Set(heatmapData.map(d => d.commodity_id))])
    .padding(0.01)

  const y = d3.scaleBand()
    .range([_height, 0])
    .domain([...new Set(heatmapData.map(d => d.vessel_id))])
    .padding(0.01)

  // 添加 X 轴
  svg.append('g')
    .attr('transform', `translate(0, ${_height})`)
    .call(d3.axisBottom(x))

  // 添加 Y 轴
  svg.append('g')
    .call(d3.axisLeft(y))

  // 设置颜色比例尺
  const colorScale = d3.scaleSequential(d3.interpolateBlues)
    .domain([0, d3.max(heatmapData, d => d.frequency)])

  // 绘制热力图的方块
  svg.selectAll()
    .data(heatmapData)
    .enter()
    .append('rect')
    .attr('x', d => x(d.commodity_id))
    .attr('y', d => y(d.vessel_id))
    .attr('width', x.bandwidth())
    .attr('height', y.bandwidth())
    .style('fill', d => colorScale(d.frequency))

  // 添加方块上的文本
  // svg.selectAll()
  //   .data(heatmapData)
  //   .enter()
  //   .append('text')
  //   .attr('x', d => x(d.vessel_id) + x.bandwidth() / 2)
  //   .attr('y', d => y(d.location_id) + y.bandwidth() / 2)
  //   .attr('dy', '.35em')
  //   .attr('text-anchor', 'middle')
  //   .text(d => d.frequency)
}

watch([frequencyCommodityVessels], ([newFrequencyCommodityVessels]) => {
  if (newFrequencyCommodityVessels.length > 0)
    drawHeatmap(newFrequencyCommodityVessels)
}, { immediate: true })
</script>

<template>
  <div id="heatmap3" />
</template>

<style scoped>
#heatmap {
  font-family: Arial, sans-serif;
}
</style>
