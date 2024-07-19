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
const { vesselMovements, selectedVesselIDs, selectedLocationIDs, dateInterval } = storeToRefs(store)

function frequencyVesselLocations(vesselMovements) {
  const frequencyDict: any = {}
  // 计算每个船只在每个地点出现的次数
  for (const movement of vesselMovements) {
    const { vessel_id, location_id } = movement
    if (!frequencyDict[vessel_id])
      frequencyDict[vessel_id] = {}
    if (!frequencyDict[vessel_id][location_id])
      frequencyDict[vessel_id][location_id] = 0
    frequencyDict[vessel_id][location_id] += 1
  }

  // 转换为所需的数组格式
  const frequencyArray = []
  for (const vessel_id in frequencyDict) {
    for (const location_id in frequencyDict[vessel_id]) {
      frequencyArray.push({
        vessel_id,
        location_id,
        frequency: frequencyDict[vessel_id][location_id],
      })
    }
  }

  return frequencyArray
}

function drawHeatmap(vesselMovements, selectedVesselIDs, selectedLocationIDs, dateInterval) {
  const filterVesselMovements = vesselMovements.filter((d: any) => {
    return selectedVesselIDs.includes(d.vessel_id)
      && selectedLocationIDs.includes(d.location_id)
      && d3.timeParse('%Y-%m-%d')(dateInterval[0]) <= d3.timeParse('%Y-%m-%dT%H:%M:%S')(d.start_time)
      && d3.timeParse('%Y-%m-%dT%H:%M:%S')(d.start_time) <= d3.timeParse('%Y-%m-%d')(dateInterval[1])
  })
  const heatmapData = frequencyVesselLocations(filterVesselMovements)

  const margin = { top: 5, right: 5, bottom: 5, left: 5 }
  // 设置 SVG 画布
  const _width = width - margin.left - margin.right
  const _height = height - margin.top - margin.bottom
  d3.select('#heatmap').selectAll('*').remove()
  const svg = d3.select('#heatmap')
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // 设置 X 和 Y 轴的刻度
  const x = d3.scaleBand()
    .range([0, _width])
    .domain([...new Set(heatmapData.map(d => d.location_id))])
    .padding(0.01)

  const y = d3.scaleBand()
    .range([_height, 0])
    .domain([...new Set(heatmapData.map(d => d.vessel_id))])
    .padding(0.01)

  // 添加 X 轴
  //   svg.append('g')
  //     .attr('transform', `translate(0, ${_height})`)
  //     .call(d3.axisBottom(x))

  // 添加 Y 轴
  //   svg.append('g')
  //     .call(d3.axisLeft(y))

  // 设置颜色比例尺
  const colorScale = d3.scaleSequential(d3.interpolateBlues)
    .domain([0, d3.max(heatmapData, d => d.frequency)])

    // Tooltip div
    const tooltip = d3.select('body')
    .append('div')
    .style('position', 'absolute')
    .style('background', '#fff')
    .style('border', '1px solid #000')
    .style('padding', '5px')
    .style('display', 'none')
    .style('pointer-events', 'none')


  // 绘制热力图的方块
  svg.selectAll()
    .data(heatmapData)
    .enter()
    .append('rect')
    .attr('x', d => x(d.location_id))
    .attr('y', d => y(d.vessel_id))
    .attr('width', x.bandwidth())
    .attr('height', y.bandwidth())
    .style('fill', d => colorScale(d.frequency))
    .on('mouseover', function (event, d: any) {
      tooltip.style('display', 'block')
        .html(`Vessel ID: ${d.vessel_id}<br>Location ID: ${d.location_id}<br>Frequency: ${d.frequency}`)
      d3.select(this).classed('box', true)
      d3.select(this).attr('stroke', 'black')
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
      d3.select(this).attr('stroke', 'none')
    })

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

watch([vesselMovements, selectedVesselIDs, selectedLocationIDs, dateInterval], ([newVesselMovements, newSelectedVesselIDs, newSelectedLocationIDs, newDateInterval]) => {
  if (newVesselMovements.length > 0
    && newSelectedVesselIDs.length > 0
    && newSelectedLocationIDs.length > 0
    && d3.timeParse('%Y-%m-%d')('2035-2-1') <= d3.timeParse('%Y-%m-%d')(newDateInterval[0])
    && d3.timeParse('%Y-%m-%d')(newDateInterval[1]) <= d3.timeParse('%Y-%m-%d')('2035-12-31')
  )
    drawHeatmap(newVesselMovements, newSelectedVesselIDs, newSelectedLocationIDs, newDateInterval)
}, { immediate: true })
</script>

<template>
  <div id="heatmap" />
</template>

<style scoped>
#heatmap {
  font-family: Arial, sans-serif;
}
</style>
