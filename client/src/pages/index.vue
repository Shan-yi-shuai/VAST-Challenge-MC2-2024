<script setup lang="ts" generic="T extends any, O extends any">
import TheComponent from '~/components/TheComponent.vue';
import TheMainView2 from '~/components/TheMainView2.vue';
import TheMainView from '~/components/TheMainView.vue';
import { useStore } from '../stores/store'
// import { storeToRefs } from 'pinia'
// import TheVesselMovementMap from '~/components/TheVesselMovementMap.vue';
import TheCommodityDistributionMap from '~/components/TheCommodityDistributionMap.vue';
import TheCommodityLocationHeatmap from '~/components/TheCommodityLocationHeatmap.vue';
import TheVesselLocationHeatmap from '~/components/TheVesselLocationHeatmap.vue';
import TheCommodityVesselHeatmap from '~/components/TheCommodityVesselHeatmap.vue';
// import TheVesselLineChart from '~/components/TheVesselLineChart.vue';
import TheCommodityScatterPlot from '~/components/TheCommodityScatterPlot.vue';
import TheVesselSelector from '~/components/TheVesselSelector.vue';
import TheLocationSelector from '~/components/TheLocationSelector.vue';
import TheCommoditySelector from '~/components/TheCommoditySelector.vue';
import TheDateSelector from '~/components/TheDateSelector.vue';
import TheVesselCommodityUnionBox from '~/components/TheVesselCommodityUnionBox.vue';
import TheVesselCommodityRelationBox from '~/components/TheVesselCommodityRelationBox.vue';
import ThePairPanel from '~/components/ThePairPanel.vue';
import TheCommodityDistributionView from '~/components/TheCommodityDistributionView.vue';

defineOptions({
  name: 'IndexPage',
})

const store = useStore()

onMounted(() => {
  store.getVesselMovements()
  store.getVesselTSNE()
  store.getAggregatedVesselMovements()
})


const mainViewContainer = ref(null)
const mainViewWidth = ref(0)
const mainViewHeight = ref(0)

const mainView1Container = ref(null)
const mainView1Width = ref(0)
const mainView1Height = ref(0)

const aggregatedVesselMovementViewContainer = ref(null)
const aggregatedVesselMovementViewWidth = ref(0)
const aggregatedVesselMovementViewHeight = ref(0)

const vesselMovementMapContainer = ref(null)
const vesselMovementMapWidth = ref(0)
const vesselMovementMapHeight = ref(0)

const focusVesselMovementMapContainer = ref(null)
const focusVesselMovementMapWidth = ref(0)
const focusVesselMovementMapHeight = ref(0)

const matchResultContainer = ref(null)
const matchResultWidth = ref(0)
const matchResultHeight = ref(0)

const commodityLocationHeatmapContainer = ref(null)
const commodityLocationHeatmapWidth = ref(0)
const commodityLocationHeatmapHeight = ref(0)

const vesselLocationHeatmapContainer = ref(null)
const vesselLocationHeatmapWidth = ref(0)
const vesselLocationHeatmapHeight = ref(0)

const vesselLocationHeatmap2Container = ref(null)
const vesselLocationHeatmap2Width = ref(0)
const vesselLocationHeatmap2Height = ref(0)

const commodityVesselHeatmapContainer = ref(null)
const commodityVesselHeatmapWidth = ref(0)
const commodityVesselHeatmapHeight = ref(0)

const odChordContainer = ref(null)
const odChordContainerWidth = ref(0)
const odChordContainerHeight = ref(0)

const odChord2Container = ref(null)
const odChord2ContainerWidth = ref(0)
const odChord2ContainerHeight = ref(0)

const regionAverageDurationViewContainer = ref(null)
const regionAverageDurationViewWidth = ref(0)
const regionAverageDurationViewHeight = ref(0)

const vesselTSNEContainer = ref(null)
const vesselTSNEWidth = ref(0)
const vesselTSNEHeight = ref(0)

onMounted(() => {
  if (mainViewContainer.value) {
    const observer = new ResizeObserver(entries => {
      for (let entry of entries) {
        if (entry.target === mainViewContainer.value) {
          const rect = entry.contentRect
          mainViewWidth.value = rect.width
          mainViewHeight.value = rect.height
        }
      }
    })
    observer.observe(mainViewContainer.value)
  }

  if (mainView1Container.value) {
    const observer = new ResizeObserver(entries => {
      for (let entry of entries) {
        if (entry.target === mainView1Container.value) {
          const rect = entry.contentRect
          mainView1Width.value = rect.width
          mainView1Height.value = rect.height
        }
      }
    })
    observer.observe(mainView1Container.value)
  }

  if (aggregatedVesselMovementViewContainer.value) {
    const observer = new ResizeObserver(entries => {
      for (let entry of entries) {
        if (entry.target === aggregatedVesselMovementViewContainer.value) {
          const rect = entry.contentRect
          aggregatedVesselMovementViewWidth.value = rect.width
          aggregatedVesselMovementViewHeight.value = rect.height
        }
      }
    })
    observer.observe(aggregatedVesselMovementViewContainer.value)
  }

  if (vesselMovementMapContainer.value) {
    const observer = new ResizeObserver(entries => {
      for (let entry of entries) {
        if (entry.target === vesselMovementMapContainer.value) {
          const rect = entry.contentRect
          vesselMovementMapWidth.value = rect.width
          vesselMovementMapHeight.value = rect.height
        }
      }
    })
    observer.observe(vesselMovementMapContainer.value)
  }

  if (focusVesselMovementMapContainer.value) {
    const observer = new ResizeObserver(entries => {
      for (let entry of entries) {
        if (entry.target === focusVesselMovementMapContainer.value) {
          const rect = entry.contentRect
          focusVesselMovementMapWidth.value = rect.width
          focusVesselMovementMapHeight.value = rect.height
        }
      }
    })
    observer.observe(focusVesselMovementMapContainer.value)
  }

  if (matchResultContainer.value) {
    const observer = new ResizeObserver(entries => {
      for (let entry of entries) {
        if (entry.target === matchResultContainer.value) {
          const rect = entry.contentRect
          matchResultWidth.value = rect.width
          matchResultHeight.value = rect.height
        }
      }
    })
    observer.observe(matchResultContainer.value)
  }

  if (commodityLocationHeatmapContainer.value) {
    const observer = new ResizeObserver(entries => {
      for (let entry of entries) {
        if (entry.target === commodityLocationHeatmapContainer.value) {
          const rect = entry.contentRect
          commodityLocationHeatmapWidth.value = rect.width
          commodityLocationHeatmapHeight.value = rect.height
        }
      }
    })
    observer.observe(commodityLocationHeatmapContainer.value)
  }

  if (vesselLocationHeatmapContainer.value) {
    const observer = new ResizeObserver(entries => {
      for (let entry of entries) {
        if (entry.target === vesselLocationHeatmapContainer.value) {
          const rect = entry.contentRect
          vesselLocationHeatmapWidth.value = rect.width
          vesselLocationHeatmapHeight.value = rect.height
        }
      }
    })
    observer.observe(vesselLocationHeatmapContainer.value)
  }

  if (commodityVesselHeatmapContainer.value) {
    const observer = new ResizeObserver(entries => {
      for (let entry of entries) {
        if (entry.target === commodityVesselHeatmapContainer.value) {
          const rect = entry.contentRect
          commodityVesselHeatmapWidth.value = rect.width
          commodityVesselHeatmapHeight.value = rect.height
        }
      }
    })
    observer.observe(commodityVesselHeatmapContainer.value)
  }

  if (regionAverageDurationViewContainer.value) {
    const observer = new ResizeObserver(entries => {
      for (let entry of entries) {
        if (entry.target === regionAverageDurationViewContainer.value) {
          const rect = entry.contentRect
          regionAverageDurationViewWidth.value = rect.width
          regionAverageDurationViewHeight.value = rect.height
        }
      }
    })
    observer.observe(regionAverageDurationViewContainer.value)
  }

  if (odChordContainer.value) {
    const observer = new ResizeObserver(entries => {
      for (let entry of entries) {
        if (entry.target === odChordContainer.value) {
          const rect = entry.contentRect
          odChordContainerWidth.value = rect.width
          odChordContainerHeight.value = rect.height
        }
      }
    })
    observer.observe(odChordContainer.value)
  }

  if (odChord2Container.value) {
    const observer = new ResizeObserver(entries => {
      for (let entry of entries) {
        if (entry.target === odChord2Container.value) {
          const rect = entry.contentRect
          odChord2ContainerWidth.value = rect.width
          odChord2ContainerHeight.value = rect.height
        }
      }
    })
    observer.observe(odChord2Container.value)
  }

  if (vesselTSNEContainer.value) {
    const observer = new ResizeObserver(entries => {
      for (let entry of entries) {
        if (entry.target === vesselTSNEContainer.value) {
          const rect = entry.contentRect
          vesselTSNEWidth.value = rect.width
          vesselTSNEHeight.value = rect.height
        }
      }
    })
    observer.observe(vesselTSNEContainer.value)
  }

  if (vesselLocationHeatmap2Container.value) {
    const observer = new ResizeObserver(entries => {
      for (let entry of entries) {
        if (entry.target === vesselLocationHeatmap2Container.value) {
          const rect = entry.contentRect
          vesselLocationHeatmap2Width.value = rect.width
          vesselLocationHeatmap2Height.value = rect.height
        }
      }
    })
    observer.observe(vesselLocationHeatmap2Container.value)
  }
})
</script>

<template>
  <div class="m-1 h-10 w-[calc(100%-0.5rem)] flex border-1 border-slate-50 bg-white p-1">
    <TheVesselSelector />
    <TheLocationSelector />
    <TheCommoditySelector />
    <TheDateSelector />
  </div>
  <div class="m-1 h-6 w-[calc(100%-0.5rem)] flex border-1 border-slate-50 bg-white p-1">
    <TheLocationLegend />
  </div>
  <div class="m-1 h-6 w-[calc(100%-0.5rem)] flex border-1 border-slate-50 bg-white p-1">
      <TheCommodityLegend />
  </div>
  <div class="m-1 h-6 w-[calc(100%-0.5rem)] flex border-1 border-slate-50 bg-white p-1">
      <TheVesselTypeLegend />
  </div>


  <div class="m-1 h-[calc(100%-8.25rem)] w-[calc(100%-0.5rem)] flex border-1 border-slate-50 bg-white ">
    <div class="h-full w-[calc(20%-0.25rem)] flex-shrink-0 bg-slate-50 p-1">
      <div class="mb-1 h-[calc(40%-0.25rem)] w-full bg-white" ref="vesselTSNEContainer">
        <TheVesselTSNE :width="vesselTSNEWidth" :height="vesselTSNEHeight" />
      </div>
      <div class="h-30% w-full flex bg-white" ref="odChordContainer">
        <TheODChord :width="odChordContainerWidth" :height="odChordContainerHeight" />
      </div>
      <div class="h-30% w-full flex bg-white" ref="odChord2Container">
        <TheFocusODChord :width="odChord2ContainerWidth" :height="odChord2ContainerHeight" />
      </div>
    </div>
    
    <div class="h-full w-[calc(60%-0.25rem)] flex-shrink-0 bg-slate-50 p-1">
      <div class="h-35% w-full bg-white " ref="mainViewContainer">
        <TheMainView2 :width="mainViewWidth" :height="mainViewHeight" />
      </div>
      <div class="mb-1 h-[calc(10%-0.25rem)] w-full bg-white " ref="aggregatedVesselMovementViewContainer">
        <TheAggregatedVesselMovementView :width="aggregatedVesselMovementViewWidth"
          :height="aggregatedVesselMovementViewHeight" />
      </div>
      <div class="mb-1 h-[calc(20%-0.25rem)] w-full bg-white " ref="vesselLocationHeatmapContainer">
        <TheMainView
            :width="vesselLocationHeatmapWidth"
            :height="vesselLocationHeatmapHeight"
          />
      </div>
      <div class="h-20% w-full bg-white " ref="matchResultContainer">
        <TheMatchResults :width="matchResultWidth" :height="matchResultHeight" />
      </div>
      <div class="h-15% w-full flex bg-white" ref="mainView1Container">
        <TheAggregatedCommodityDistributionView :width="mainView1Width" :height="mainView1Height" />
      </div>
    </div>
    <div class="h-full w-20% flex-shrink-0 bg-slate-50 p-1">
      <div class="mb-1 h-[calc(40%-0.25rem)] w-full bg-white" ref="regionAverageDurationViewContainer">
        <TheRegionAverageDurationView
          :width="regionAverageDurationViewWidth"
          :height="regionAverageDurationViewHeight"
        />
      </div>
      <div class="h-30% w-full flex bg-white" ref="vesselMovementMapContainer">
        <TheVesselMovementMap :width="vesselMovementMapWidth" :height="vesselMovementMapHeight" />
      </div>
      <div class="h-30% w-full flex bg-white" ref="focusVesselMovementMapContainer">
        <TheFocusVesselMovementMap :width="focusVesselMovementMapWidth" :height="focusVesselMovementMapHeight" />
      </div>
    </div>
  </div>

</template>
