<script lang="ts" setup>
import { Icon } from '@iconify/vue'
import { storeToRefs } from 'pinia'
import * as d3 from 'd3'
import { useStore } from '../stores/store'

const {
  data,
} = defineProps({
  data: { default: null, type: Object },
})
const store = useStore()
const { locationIDs, vesselTypes, commodityIDs, vesselID2Vessel, selectedVesselIDs, selectedCommodityIDs, dateInterval, vessels, commoditys } = storeToRefs(store)


// const data = {
//   "date": "2035-02-04",
//   "location_id": "City of Himark",
//   "commoditys": [
//     {
//       "document_id": "cargo_2035_24532325",
//       "commodity_id": "labridaenrefert9be",
//       "qty_tons": 51.00000000000001
//     },
//     {
//       "document_id": "cargo_2035_25112180",
//       "commodity_id": "labridaenrefert9be",
//       "qty_tons": 3.0
//     }
//   ],
//   "vessels": [
//     {
//       "movement_id": "hewey2ef_City of Himark_2035-02-04T00:40:47",
//       "vessel_id": "hewey2ef",
//       "key": "hewey2ef_City of Himark_2035-02-04T00:40:47"
//     },
//     {
//       "movement_id": "tenchtaker595_City of Himark_2035-02-04T04:55:54",
//       "vessel_id": "tenchtaker595",
//       "key": "tenchtaker595_City of Himark_2035-02-03T04:55:54"
//     },
//     {
//       "movement_id": "brooktroutbuccaneerc0b_City of Himark_2035-02-04T05:10:40",
//       "vessel_id": "brooktroutbuccaneerc0b",
//       "key": "brooktroutbuccaneerc0b_City of Himark_2035-02-03T05:10:40"
//     },
//     {
//       "movement_id": "seahunter56b_City of Himark_2035-02-04T06:01:07",
//       "vessel_id": "seahunter56b",
//       "key": "seahunter56b_City of Himark_2035-02-03T06:01:07"
//     },
//     {
//       "movement_id": "skipjacktunaseeker76c_City of Himark_2035-02-04T06:02:11",
//       "vessel_id": "skipjacktunaseeker76c",
//       "key": "skipjacktunaseeker76c_City of Himark_2035-02-04T06:02:11"
//     },
//     {
//       "movement_id": "carpcatcher3f4_City of Himark_2035-02-04T08:27:43",
//       "vessel_id": "carpcatcher3f4",
//       "key": "carpcatcher3f4_City of Himark_2035-02-04T08:27:43"
//     },
//     {
//       "movement_id": "catchcruisera94_City of Himark_2035-02-04T10:09:46",
//       "vessel_id": "catchcruisera94",
//       "key": "catchcruisera94_City of Himark_2035-02-04T10:09:46"
//     },
//     {
//       "movement_id": "bluecatfishcatcher468_City of Himark_2035-02-04T16:33:35",
//       "vessel_id": "bluecatfishcatcher468",
//       "key": "bluecatfishcatcher468_City of Himark_2035-02-03T16:33:35"
//     },
//     {
//       "movement_id": "stout369_City of Himark_2035-02-04T16:47:55",
//       "vessel_id": "stout369",
//       "key": "stout369_City of Himark_2035-02-02T16:47:55"
//     },
//     {
//       "movement_id": "himarkroyal032_City of Himark_2035-02-04T19:01:20",
//       "vessel_id": "himarkroyal032",
//       "key": "himarkroyal032_City of Himark_2035-02-03T19:01:20"
//     },
//     {
//       "movement_id": "carpcapturer993_City of Himark_2035-02-04T22:08:14",
//       "vessel_id": "carpcapturer993",
//       "key": "carpcapturer993_City of Himark_2035-02-03T22:08:14"
//     },
//     {
//       "movement_id": "wavewranglerc2d_City of Himark_2035-02-04T22:10:17",
//       "vessel_id": "wavewranglerc2d",
//       "key": "wavewranglerc2d_City of Himark_2035-02-03T22:10:17"
//     }
//   ]
// }

const colorRange = d3.schemeSet3.concat(d3.schemeTableau10, d3.schemePastel1)
const locationColor = d3.scaleOrdinal(colorRange).domain(locationIDs.value)

const typeColor = d3.scaleOrdinal(d3.schemeCategory10)
  .domain(vesselTypes.value)

const commodityColor = d3.scaleOrdinal(d3.schemeSet1)
  .domain(commodityIDs.value)

const selectedVessel = ref(null as any)
const selectedCommodity = ref(null as any)

const clickedVessel = ref(null as any)
const clickedCommodity = ref(null as any)

function getDateRange(dateStr: string, days: number = 7) {
  const inputDate = new Date(dateStr)
  const startDate = new Date('2035-02-01')
  const endDate = new Date('2035-12-31')

  // Calculate one week in milliseconds
  const duration = days * 24 * 60 * 60 * 1000

  // Calculate previous week and next week
  let previousDate = new Date(inputDate.getTime() - duration)
  let nextDate = new Date(inputDate.getTime() + duration)

  // Ensure previous week is not before the start date
  if (previousDate < startDate) {
    previousDate = startDate
  }

  // Ensure next week is not after the end date
  if (nextDate > endDate) {
    nextDate = endDate
  }

  // Format the dates to YYYY-MM-DD
  const formatDate = (date: any) => date.toISOString().split('T')[0];

  return [formatDate(previousDate), formatDate(nextDate)];
}

const clickVessel = (vessel: any) => {
  if (clickedVessel.value?.movement_id === vessel.movement_id) {
    clickedVessel.value = null
    selectedVesselIDs.value = vessels.value.map((vessel: any) => vessel.id)
  }
  else {
    clickedVessel.value = vessel
    selectedVesselIDs.value = [vessel.vessel_id]
    dateInterval.value = getDateRange(data.date)
  }
  if (clickedVessel.value === null && clickedCommodity.value === null) {
    store.initialization()
  }
}

const clickCommodity = (commodity: any) => {
  if (clickedCommodity.value?.document_id === commodity.document_id) {
    clickedCommodity.value = null
    selectedCommodityIDs.value = commoditys.value.map((commodity: any) => commodity.id)
  }
  else {
    clickedCommodity.value = commodity
    selectedCommodityIDs.value = [commodity.commodity_id]
    dateInterval.value = getDateRange(data.date)
  }
  if (clickedVessel.value === null && clickedCommodity.value === null) {
    store.initialization()
  }

}

const linkVessel = (vessel: any) => {
  selectedVessel.value = vessel
  if (selectedCommodity.value !== null) {
    store.addVesselCommodityPair(data.date, data.location_id, selectedVessel.value, selectedCommodity.value)
    selectedVessel.value = null
    selectedCommodity.value = null
  }
}

const linkCommodity = (commodity: any) => {
  selectedCommodity.value = commodity
  if (selectedVessel.value !== null) {
    store.addVesselCommodityPair(data.date, data.location_id, selectedVessel.value, selectedCommodity.value)
    selectedVessel.value = null
    selectedCommodity.value = null
  }
}
</script>

<template>
  <div class="w-full h-full">
    <div class="w-full h-6 flex b-2 border-gray-200 items-center gap-2 px-2 py-0.5 text-xs">
      <div class="bg-slate-300 h-full rounded-md px-2 flex">{{ data.date }}</div>
      <div :style="{ backgroundColor: locationColor(data.location_id) }" class="h-full rounded-md px-2 flex">
        {{ data.location_id }}
      </div>
    </div>
    <div class="w-full h-[calc(100%-1.5rem)] flex b-2 border-gray-200 text-xs overflow-y-auto">
      <div class="w-50% h-full overflow-y-auto overflow-x-hidden py-0.5 mr-2 border-gray-200 b-1">
        <div v-for="commodity in data.commoditys" :key="commodity.document_id"
          class="w-full bg-slate-100 m-1 p-1 overflow-x-auto flex" @click.stop="clickCommodity(commodity)"
          :style="{ backgroundColor: clickedCommodity?.document_id === commodity.document_id ? 'lightblue' : 'white' }">
          <div class="w-[calc(100%-2rem)] overflow-x-auto">
            <div class="w-full flex mb-1">
              commodity_id: <div :style="{ backgroundColor: commodityColor(commodity.commodity_id) }"
                class="h-full rounded-md px-2 flex ml-2">{{ commodity.commodity_id }}</div>
            </div>
            <div class="w-full flex">
              qty_tons: <div class="h-full rounded-md px-2 flex ml-2 bg-slate-300">{{ commodity.qty_tons }}</div>
            </div>
          </div>
          <div class="w-8">
            <button class="icon-btn rounded w-8 h-full flex items-center justify-center"
              :style="{ backgroundColor: selectedCommodity?.document_id === commodity.document_id ? 'steelblue' : 'white' }"
              @click.stop="linkCommodity(commodity)">
              <Icon icon="nimbus:link" width="16" height="16" />
            </button>
          </div>
        </div>
      </div>
      <div class="w-[calc(50%-0.5rem)] h-full overflow-y-auto overflow-x-hidden gap-2 py-0.5 border-gray-200 b-1">
        <div v-for="vessel in data.vessels" :key="vessel.movement_id"
          class="w-full bg-slate-100 m-1 p-1 overflow-x-auto flex" @click.stop="clickVessel(vessel)"
          :style="{ backgroundColor: clickedVessel?.movement_id === vessel.movement_id ? 'lightblue' : 'white' }">
          <div class="w-[calc(100%-2rem)] overflow-x-auto">
            <div class="w-full flex mb-1">
              vessel_id: <div :style="{ backgroundColor: typeColor(vesselID2Vessel[vessel.vessel_id].type) }"
                class="h-full rounded-md px-2 flex ml-2">{{ vessel.vessel_id }}</div>
            </div>
            <div class="w-full flex" v-if="vesselID2Vessel[vessel.vessel_id].tonnage">
              vessel_tonnage: <div class="h-full rounded-md px-2 flex ml-2 bg-slate-300">{{
        vesselID2Vessel[vessel.vessel_id].tonnage }}</div>
            </div>
          </div>
          <div class="w-8">
            <button class="icon-btn rounded w-8 h-full flex items-center justify-center"
              :style="{ backgroundColor: selectedVessel?.movement_id === vessel.movement_id ? 'steelblue' : 'white' }"
              @click.stop="linkVessel(vessel)">
              <Icon icon="nimbus:link" width="16" height="16" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>