<script setup lang='ts'>
import { storeToRefs } from 'pinia'
import * as d3 from 'd3'
import { watch } from 'vue'
import { useStore } from '../stores/store'
import { on } from 'events';

interface CommodityDistribution {
  date: string | Date
  commodity_id: string
  location_id: string
  qty_tons: number
}

interface AggregatedDetail {
  location_id: string
  qty_tons: number
  count: number
}

interface CombinedData {
  date: string | Date
  commodity_id: string
  details: { location_id: string; qty_tons: number }[]
  aggregatedDetails?: AggregatedDetail[]
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
const { transportMovements, pairVesselCommodity, selectedVesselIDs, selectedLocationIDs, selectedCommodityIDs, dateInterval, commodityIDs, focusVesselID, locationColor, locationID2Name, commodityID2Name } = storeToRefs(store)

function transformData(data: any): any {
  const result: any = []

  data.forEach(item => {
    const existing = result.find(
      res => (res.date === item.date && res.commodity_id === item.commodity.commodity_id)
    )

    if (existing) {
      existing.details.push({
        location_id: item.location_id,
        qty_tons: item.commodity.qty_tons,
      })
    }
    else {
      result.push({
        date: item.date,
        commodity_id: item.commodity.commodity_id,
        details: [
          {
            location_id: item.location_id,
            qty_tons: item.commodity.qty_tons,
          },
        ],
      })
    }
  })
  // 计算每个条目的聚合详细信息
  result.forEach(item => {
    item.aggregatedDetails = aggregateDetails(item.details).sort((a, b) => b.count - a.count)
  })

  return result
}

function aggregateDetails(details: { location_id: string; qty_tons: number }[]) {
  const aggregated = details.reduce((acc, detail) => {
    const key = detail.location_id
    if (!acc[key]) {
      acc[key] = {
        location_id: key,
        qty_tons: 0,
        count: 0,
      }
    }
    acc[key].qty_tons += detail.qty_tons
    acc[key].count += 1
    return acc
  }, {} as Record<string, { qty_tons: number; count: number }>)

  return Object.values(aggregated)
}

function renderChart(originalTransportMovements: any, originalCommodityDistributions: any, focusVesselID: any, selectedVesselIDs: any, selectedLocationIDs: any, selectedCommodityIDs: any, dateInterval: any): void {
  let aggregatedFlag = true
  if (selectedLocationIDs.length === 1)
    aggregatedFlag = false
  const commodityDistributions = originalCommodityDistributions.filter((d: any) => selectedLocationIDs.includes(d.location_id)).filter((d: any) => selectedCommodityIDs.includes(d.commodity.commodity_id)).filter((d: any) => selectedVesselIDs.includes(d.vessel.vessel_id)).filter((d: any) => d3.timeParse('%Y-%m-%d')(dateInterval[0]) <= d3.timeParse('%Y-%m-%d')(d.date) && d3.timeParse('%Y-%m-%d')(d.date) <= d3.timeParse('%Y-%m-%d')(dateInterval[1]))

  const commodityDistributionsCopy = JSON.parse(JSON.stringify(commodityDistributions))

  const parseDate2 = d3.timeParse('%Y-%m-%d')
  const formatDateToDay = (date: any) => d3.timeFormat('%Y-%m-%d')(date)

  const combinedData = transformData(commodityDistributionsCopy)
  combinedData.forEach((d: any) => d.date = parseDate2(formatDateToDay(parseDate2(d.date))))

  const margin = { top: 10, right: 10, bottom: 10, left: 20 }
  const _width = width - margin.left - margin.right
  const _height = height - margin.top - margin.bottom

  d3.select('#chart4').selectAll('*').remove()
  const svg = d3.select('#chart4')
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // 设置时间轴范围
  const x = d3.scaleTime()
    .domain(dateInterval.map((d: string) => d3.timeParse('%Y-%m-%d')(d)) as [Date, Date])
    .range([0, _width-40])

  const yCommodity = d3.scaleBand()
    .domain(commodityIDs.value)
    .range([0, _height - 10])
    .padding(0.1)

  const addition = 2
  const colorAggregated = d3.scaleLog()
    .domain([1, d3.max(combinedData, d => d.details.length) + addition || 10])
    .interpolate(() => d3.interpolateBlues)

  // 绘制时间轴
  svg.append('g')
    .attr('transform', `translate(0,${_height-10})`)
    .call(d3.axisBottom(x).tickFormat(d3.timeFormat('%Y-%m-%d')))
    .selectAll('text') // 选择所有文本标签
    .style('font-size', '6px') // 设置字体大小为10px

  // 绘制commodity的y轴
  svg.append('g')
    .call(d3.axisLeft(yCommodity))
    .selectAll('text')
    .attr('font-size', 3)
    .text((d: string) => `${d} (${commodityID2Name.value[d]})`)

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

  // 绘制下半部分的commodity
  svg.selectAll('.commodity')
    .data(combinedData)
    .enter().append('rect')
    .attr('class', 'bar commodity')
    .attr('x', (d: CombinedData) => x(d.date as Date))
    .attr('y', (d: CombinedData) => yCommodity(d.commodity_id) as number)
    .attr('width', barWidth) // 占至少一天的长度
    .attr('height', yCommodity.bandwidth())
    .attr('fill', (d: CombinedData) => {
      if (aggregatedFlag)
        return colorAggregated(d.details.length + addition)
      else
        return locationColor.value(d.commodity_id)
    })
    .attr('stroke', 'none')
    .on('mouseover', function (event, d: CombinedData) {
      const detailsHTML = d.aggregatedDetails.map(detail =>
        `Location: ${locationID2Name.value[detail.location_id]} Total Tons: ${detail.qty_tons} Count: ${detail.count}`
      ).join('<br>')

      tooltip.style('display', 'block')
        .html(`Date: ${d3.timeFormat('%Y-%m-%d')(d.date as Date)}<br>Commodity: ${commodityID2Name.value[d.commodity_id]}<br>${detailsHTML}`)
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

  // Brush for commodities
  const brushCommodity = d3.brushY()
    .extent([[-10, 3 * _height / 4 + 20], [10, _height]])
    .on('end', (event: any) => {
      if (!event.selection) return
      const selected = yCommodity.domain().filter(d => {
        const pos = yCommodity(d) + yCommodity.bandwidth() / 2
        return event.selection[0] <= pos && pos <= event.selection[1]
      })
      store.selectedCommodityIDs = selected
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
    .attr('class', 'brushCommodity')
    .call(brushCommodity)

  svg.append('g')
    .attr('class', 'brushX')
    .call(brushX)
}

watch([transportMovements, focusVesselID, selectedVesselIDs, selectedLocationIDs, selectedCommodityIDs, dateInterval], ([newTransportMovements, newFocusVesselID, newSelectedVesselIDs, newSelectedLocationIDs, newSelectedCommodityIDs, newDateInterval]) => {
  if (newTransportMovements.length > 0
    && newSelectedVesselIDs.length > 0
    && newSelectedLocationIDs.length > 0
    && newSelectedCommodityIDs.length > 0
    && d3.timeParse('%Y-%m-%d')('2035-2-1') <= d3.timeParse('%Y-%m-%d')(newDateInterval[0])
    && d3.timeParse('%Y-%m-%d')(newDateInterval[1]) <= d3.timeParse('%Y-%m-%d')('2035-12-31')
  )
    renderChart(transportMovements.value, pairVesselCommodity.value, newFocusVesselID, newSelectedVesselIDs, newSelectedLocationIDs, newSelectedCommodityIDs, newDateInterval)
}, { immediate: true })
</script>

<template>
  <div id="chart4" />
</template>
