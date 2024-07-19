<script setup lang='ts'>
import { storeToRefs } from 'pinia'
import * as d3 from 'd3'
import { watch } from 'vue'
import { useStore } from '../stores/store'
import { on } from 'events'

interface Commodity {
  document_id: string
  commodity_id: string
  qty_tons: number
}

interface Vessel {
  movement_id: string
  vessel_id: string
  key: string
}

interface DataItem {
  date: string | Date
  location_id: string
  commodity: Commodity
  vessel: Vessel
}

interface AggregatedDetail {
  location: string
  commodity_id: string
  qty_tons: number
  count: number
}

interface CombinedData {
  date: string | Date
  vessel_id: string
  details: { location: string; commodity: Commodity }[]
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
const { pairVesselCommodity, vesselMovements, selectedVesselIDs, selectedLocationIDs, selectedCommodityIDs, dateInterval, vesselID2Vessel, focusVesselID, vesselTypeColor, locationColor, commodityColor, vesselID2Name, locationID2Name, commodityID2Name } = storeToRefs(store)
function transformData(data: DataItem[]): CombinedData[] {
  const result: CombinedData[] = []

  data.forEach(item => {
    const existing = result.find(
      res => (res.date === item.date && res.vessel_id === item.vessel.vessel_id)
    )

    if (existing) {
      existing.details.push({
        location: item.location_id,
        commodity: item.commodity,
      })
    }
    else {
      result.push({
        date: item.date,
        vessel_id: item.vessel.vessel_id,
        details: [
          {
            location: item.location_id,
            commodity: item.commodity,
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

function aggregateDetails(details: { location: string; commodity: Commodity }[]) {
  const aggregated = details.reduce((acc, detail) => {
    const key = `${detail.location}_${detail.commodity.commodity_id}`
    if (!acc[key]) {
      acc[key] = {
        location: detail.location,
        commodity_id: detail.commodity.commodity_id,
        qty_tons: 0,
        count: 0,
      }
    }
    acc[key].qty_tons += detail.commodity.qty_tons
    acc[key].count += 1
    return acc
  }, {} as Record<string, { location: string; commodity_id: string; qty_tons: number; count: number }>)

  return Object.values(aggregated)
}

function getVesselMovementSequences(vesselMovements: any[]) {
  const vesselMovementSequences: any = {}

  vesselMovements.forEach((record) => {
    const { date, location_id, vessel, commodity } = record
    const source = record.resource ? record.resource : null

    if (!vesselMovementSequences[vessel.vessel_id])
      vesselMovementSequences[vessel.vessel_id] = []
    vesselMovementSequences[vessel.vessel_id].push([date, location_id, source, commodity])
  })

  Object.keys(vesselMovementSequences).forEach((vesselId) => {
    vesselMovementSequences[vesselId].sort((a, b) => new Date(b[0]).getTime() - new Date(a[0]).getTime())
  })

  return vesselMovementSequences
}

function getPossibleSourceLine(vesselMovementSequences: any) {
  const possibleSourceLine: any = []

  for (const vesselId in vesselMovementSequences) {
    const movements = vesselMovementSequences[vesselId]
    for (let i = 0; i < movements.length - 1; i++) {
      // const from = movements[i][1]
      // const to = movements[i + 1][1]
      // if (from === to)
      //   continue
      const source = movements[i][2]
      if (source)
        possibleSourceLine.push([vesselId, movements[i][0], movements[i + 1][0], source])
    }
  }

  return possibleSourceLine
}

function renderChart(matchResults: any, selectedVesselIDs: any, selectedLocationIDs: any, selectedCommodityIDs: any, dateInterval: any, focusVesselID: any): void {
  let aggregatedFlag = true
  if (selectedLocationIDs.length === 1)
    aggregatedFlag = false
  const filteredMatchResults = matchResults.filter((d: any) => selectedVesselIDs.includes(d.vessel.vessel_id)).filter((d: any) => selectedLocationIDs.includes(d.location_id)).filter((d: any) => selectedCommodityIDs.includes(d.commodity.commodity_id)).filter((d: any) => d3.timeParse('%Y-%m-%d')(dateInterval[0]) <= d3.timeParse('%Y-%m-%d')(d.date) && d3.timeParse('%Y-%m-%d')(d.date) <= d3.timeParse('%Y-%m-%d')(dateInterval[1]))
  const parseDate2 = d3.timeParse('%Y-%m-%d')
  const formatDateToDay = (date: any) => d3.timeFormat('%Y-%m-%d')(date)
  const filteredMatchResultsCopy = JSON.parse(JSON.stringify(filteredMatchResults))
  filteredMatchResultsCopy.forEach((d: any) => d.date = parseDate2(formatDateToDay(parseDate2(d.date))))
  // filteredMatchResultsCopy.forEach((d: any) => d.date = parseDate2(formatDateToDay(parseDate2(d.date))))
  const combinedData = transformData(filteredMatchResultsCopy)
  // combinedData.forEach((d: any) => d.date = parseDate2(formatDateToDay(parseDate2(d.date))))

  const possibleSourceLine = getPossibleSourceLine(getVesselMovementSequences(filteredMatchResultsCopy))

  const vesselIDTypes = []

  for (const key of selectedVesselIDs) {
    const vessel = vesselID2Vessel.value[key]
    vesselIDTypes.push({ vessel_id: vessel.id, vessel_type: vessel.type })
  }

  // 按类型对数据进行分组
  const grouped_data = d3.group(vesselIDTypes, (d: any) => d.vessel_type)

  // 将分组后的数据平铺为一个数组
  const sorted_vessel_data: any[] = []
  grouped_data.forEach((group: any) => {
    sorted_vessel_data.push(...group)
  })

  const index = sorted_vessel_data.findIndex(item => item.vessel_id === focusVesselID)

  if (index !== -1) {
    const [item] = sorted_vessel_data.splice(index, 1)
    sorted_vessel_data.unshift(item)
  }

  const margin = { top: 10, right: 10, bottom: 10, left: 20 }
  const _width = width - margin.left - margin.right
  const _height = height - margin.top - margin.bottom

  d3.select('#match').selectAll('*').remove()
  const svg = d3.select('#match')
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // 设置时间轴范围
  const x = d3.scaleTime()
    .domain(dateInterval.map((d: string) => d3.timeParse('%Y-%m-%d')(d)) as [Date, Date])
    .range([0, _width - 40])

  const yVessel = d3.scaleBand()
    .domain(sorted_vessel_data.map((d: any) => d.vessel_id))
    .range([0, _height - 10])
    .padding(0.1)

  // const addition = 2
  // const colorAggregated = d3.scaleLog()
  //   .domain([1, d3.max(combinedData, d => d.details.length) + addition || 10])
  //   .interpolate(() => d3.interpolateBlues)

  // 绘制时间轴
  svg.append('g')
    .attr('transform', `translate(0,${_height - 10})`)
    .call(d3.axisBottom(x).tickFormat(d3.timeFormat('%Y-%m-%d')))
    .selectAll('text') // 选择所有文本标签
    .style('font-size', '6px') // 设置字体大小为10px

  // 绘制y轴并根据vessel_type设置文本颜色
  const yAxis = svg.append('g')
    .call(d3.axisLeft(yVessel))

  yAxis.selectAll('text')
    .style('fill', d => {
      const vessel = sorted_vessel_data.find(v => v.vessel_id === d)
      return vessel ? vesselTypeColor.value(vessel.vessel_type) : 'black'
    })
    .text(d => vesselID2Name.value[d] ? vesselID2Name.value[d] : d)
    .attr('font-size', 3)

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
    .attr('y', (d: any) => yVessel(d.vessel_id) as number)
    .attr('width', barWidth) // 占至少一天的长度
    .attr('height', yVessel.bandwidth())
    .attr('fill', (d: any) => {
      return locationColor.value(d.aggregatedDetails[0].location)
      // if (aggregatedFlag) {
      //   return colorAggregated(d.details.length + addition)
      // }
      // else {
      //   if (d.details.length > 1)
      //     return 'black'
      //   return commodityColor.value(d.details[0].commodity.commodity_id)
      // }
    })
    .attr('stroke', 'none')
    .on('mouseover', function (event, d: any) {
      const detailsHTML = d.aggregatedDetails.map(detail =>
        `Location: ${locationID2Name.value[detail.location]} Commodity: ${commodityID2Name.value[detail.commodity_id]} Qty Tons: ${detail.qty_tons} Count: ${detail.count}`
      ).join('<br>')

      tooltip.style('display', 'block')
        .html(`Date: ${d3.timeFormat('%Y-%m-%d')(d.date as Date)}<br>Vessel: ${vesselID2Name.value[d.vessel_id]}<br>${detailsHTML}`)
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

  svg.selectAll('.possible-source-line')
    .data(possibleSourceLine)
    .enter().append('line')
    .attr('class', 'possible-source-line')
    .attr('x1', (d: any) => x(d[1] as Date) + barWidth / 2)
    .attr('y1', (d: any) => yVessel(d[0]) as number + yVessel.bandwidth() / 2)
    .attr('x2', (d: any) => x(d[2] as Date) + barWidth / 2)
    .attr('y2', (d: any) => yVessel(d[0]) as number + yVessel.bandwidth() / 2)
    .attr('stroke', (d: any) => locationColor.value(d[3]))
    .attr('stroke-width', yVessel.bandwidth() / 2)
    .attr('stroke-dasharray', '2,2')
    .on('mouseover', function (event, d: any) {
      tooltip.style('display', 'block')
        .html(`Possible Source: ${locationID2Name.value[d[3]]}`)
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

  // if (aggregatedFlag) {
  //   // 添加图例
  //   const legend = svg.append('g')
  //     .attr('class', 'legend')
  //     .attr('transform', `translate(${_width}, 0)`)

  //   const legendScale = d3.scaleLinear()
  //     .domain(colorAggregated.domain())
  //     .range([0, 200])

  //   const legendAxis = d3.axisRight(legendScale)
  //     .ticks(5)

  //   legend.append('g')
  //     .selectAll('rect')
  //     .data(d3.range(1, d3.max(combinedData, d => d.details.length) + addition || 10, 1))
  //     .enter().append('rect')
  //     .attr('y', (d, i) => legendScale(d))
  //     .attr('width', 20)
  //     .attr('height', legendScale(1) - legendScale(0))
  //     .attr('fill', (d) => colorAggregated(d + addition))

  //   legend.append('g')
  //     .attr('transform', `translate(20, 0)`)
  //     .call(legendAxis)

  //   legend.selectAll('text.legend-label')
  //     .data(d3.range(1, d3.max(combinedData, d => d.details.length) + addition || 10, 1))
  //     .enter().append('text')
  //     .attr('class', 'legend-label')
  //     .attr('x', 25)
  //     .attr('y', (d, i) => legendScale(d) + (legendScale(d + 1) - legendScale(d)) / 2)
  //     .attr('dy', '0.35em')
  //     .text(d => d)

  //   // 添加vessel_type的图例
  //   // const typeLegend = svg.selectAll('.type-legend')
  //   //   .data(typeColor.domain())
  //   //   .enter().append('g')
  //   //   .attr('class', 'type-legend')
  //   //   .attr('transform', (d, i) => `translate(0,${(i) * 10 + 10 + 200})`)

  //   // typeLegend.append('rect')
  //   //   .attr('x', _width)
  //   //   .attr('width', 9)
  //   //   .attr('height', 3)
  //   //   .style('fill', typeColor)

  //   // typeLegend.append('text')
  //   //   .attr('x', _width - 5)
  //   //   .attr('y', 1)
  //   //   .attr('dy', '.35em')
  //   //   .attr('font-size', 4)
  //   //   .style('text-anchor', 'end')
  //   //   .text(d => d)
  // }
  // else {
  //   // 添加图例
  //   const legend = svg.selectAll('.legend')
  //     .data(commodityColor.value.domain())
  //     .enter().append('g')
  //     .attr('class', 'legend')
  //     .attr('transform', (d: any, i: number) => `translate(0,${i * 10})`)
  //     .on('click', function (event, d: string) {
  //       const isActive = d3.select(this).classed('active')
  //       d3.selectAll('.legend').classed('active', false).select('rect').style('stroke', 'none')
  //       d3.selectAll('.bar').style('fill', (d: any) => commodityColor.value(d.commodity.commodity_id))

  //       if (!isActive) {
  //         d3.select(this).classed('active', true).select('rect').style('stroke', 'black')
  //         svg.selectAll('.bar')
  //           .filter((barData: any) => barData.commodity.commodity_id === d)
  //           .style('fill', 'black')
  //       }
  //     })

  //   legend.append('rect')
  //     .attr('x', _width)
  //     .attr('width', 9)
  //     .attr('height', 9)
  //     .style('fill', commodityColor.value)

  //   legend.append('text')
  //     .attr('x', _width - 5)
  //     .attr('y', 4)
  //     .attr('dy', '.35em')
  //     .attr('font-size', 4)
  //     .style('text-anchor', 'end')
  //     .text((d: string) => d)

  //   // 添加vessel_type的图例
  //   // const typeLegend = svg.selectAll('.type-legend')
  //   //   .data(typeColor.domain())
  //   //   .enter().append('g')
  //   //   .attr('class', 'type-legend')
  //   //   .attr('transform', (d, i) => `translate(0,${(i + color.domain().length) * 10 + 10})`)

  //   // typeLegend.append('rect')
  //   //   .attr('x', _width)
  //   //   .attr('width', 9)
  //   //   .attr('height', 3)
  //   //   .style('fill', typeColor)

  //   // typeLegend.append('text')
  //   //   .attr('x', _width - 5)
  //   //   .attr('y', 1)
  //   //   .attr('dy', '.35em')
  //   //   .attr('font-size', 4)
  //   //   .style('text-anchor', 'end')
  //   //   .text(d => d)
  // }
}

watch([vesselMovements, selectedVesselIDs, selectedLocationIDs, selectedCommodityIDs, dateInterval, focusVesselID], ([newVesselMovements, newSelectedVesselIDs, newSelectedLocationIDs, newSelectedCommodityIDs, newDateInterval, newFocusVesselID]) => {
  if (newVesselMovements.length > 0
    && newSelectedVesselIDs.length > 0
    && newSelectedLocationIDs.length > 0
    && newSelectedCommodityIDs.length > 0
    && d3.timeParse('%Y-%m-%d')('2035-2-1') <= d3.timeParse('%Y-%m-%d')(newDateInterval[0])
    && d3.timeParse('%Y-%m-%d')(newDateInterval[1]) <= d3.timeParse('%Y-%m-%d')('2035-12-31')
  )
    renderChart(pairVesselCommodity.value, newSelectedVesselIDs, newSelectedLocationIDs, newSelectedCommodityIDs, newDateInterval, newFocusVesselID)
}, { immediate: true })
</script>

<template>
  <div id="match" />
</template>
