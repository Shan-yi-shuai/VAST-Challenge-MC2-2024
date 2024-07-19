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
const { vesselMovements } = storeToRefs(store)

function drawLineChart(vesselMovements) {
  const margin = { top: 5, right: 5, bottom: 5, left: 5 }
  // 设置 SVG 画布
  const _width = width - margin.left - margin.right
  const _height = height - margin.top - margin.bottom
  const svg = d3.select('#line-chart')
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // 处理数据，将日期转换为 Date 对象
  vesselMovements.forEach(d => {
    d.date = new Date(d.date)
  })

  // 按vessel_id分组数据
  const groupedData = d3.group(vesselMovements, d => d.vessel_id)

  // 设置 X 轴和 Y 轴的刻度
  const x = d3.scaleTime()
    .domain(d3.extent(vesselMovements, d => d.date))
    .range([0, _width])

  const y = d3.scalePoint()
    .domain([...new Set(vesselMovements.map(d => d.location_id))])
    .range([_height, 0])

  // 添加 X 轴
  svg.append('g')
    .attr('transform', `translate(0, ${_height})`)
    .call(d3.axisBottom(x))

  // 添加 Y 轴
  svg.append('g')
    .call(d3.axisLeft(y))

  // 创建线生成器
  const line = d3.line()
    .x(d => x(d.date))
    .y(d => y(d.location_id))

  // 绘制每个 vessel 的折线图
  groupedData.forEach((data, vessel_id) => {
    svg.append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', () => d3.schemeCategory10[vessel_id.charCodeAt(0) % 10])
      .attr('stroke-width', 1.5)
      .attr('d', line)

    // 添加数据点
    // svg.selectAll(`.dot-${vessel_id}`)
    //   .data(data)
    //   .enter().append('circle')
    //   .attr('class', `dot-${vessel_id}`)
    //   .attr('cx', d => x(d.date))
    //   .attr('cy', d => y(d.location_id))
    //   .attr('r', 3)
    //   .attr('fill', () => d3.schemeCategory10[vessel_id.charCodeAt(0) % 10])
    //   .append('title')
    //   .text(d => `Date: ${d.date.toISOString().split('T')[0]}, Location: ${d.location_id}`)
  })
}

watch([vesselMovements], ([newVesselMovements]) => {
  if (newVesselMovements.length > 0)
    drawLineChart(newVesselMovements)
}, { immediate: true })
</script>

<template>
  <div id="line-chart" />
</template>

<style scoped>
#heatmap {
  font-family: Arial, sans-serif;
}
</style>
