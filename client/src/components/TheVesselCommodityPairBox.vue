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
const { locationIDs, vesselTypes, commodityIDs, vesselID2Vessel } = storeToRefs(store)


// const data = {
//   "date": "2035-02-26",
//   "location_id": "City of Haacklee",
//   "vessel": {
//     "movement_id": "bluegillbandita5f_City of Haacklee_2035-02-26T04:16:39",
//     "vessel_id": "bluegillbandita5f",
//     "key": "bluegillbandita5f_City of Haacklee_2035-02-24T04:16:39"
//   },
//   "commodity": {
//     "document_id": "cargo_2035_27038e62",
//     "commodity_id": "labridaenrefert9be",
//     "qty_tons": -0.75
//   }
// }

const colorRange = d3.schemeSet3.concat(d3.schemeTableau10, d3.schemePastel1)
const locationColor = d3.scaleOrdinal(colorRange).domain(locationIDs.value)

const typeColor = d3.scaleOrdinal(d3.schemeCategory10)
  .domain(vesselTypes.value)

const commodityColor = d3.scaleOrdinal(d3.schemeSet1)
  .domain(commodityIDs.value)
</script>

<template>
  <div class="w-full">
    <div class="w-full h-6 flex b-2 border-gray-200 items-center gap-2 px-2 py-0.5 text-xs">
      <div class="bg-slate-300 h-full rounded-md px-2 flex">{{ data.date }}</div>
      <div :style="{ backgroundColor: locationColor(data.location_id) }" class="h-full rounded-md px-2 flex">
        {{ data.location_id }}
      </div>
      <div class="ml-auto flex items-center">

        <button class="icon-btn rounded w-8 h-full flex items-center justify-center"
          @click="$emit('deletePair', data)">
          <Icon icon="nimbus:trash"/>
        </button>
      </div>
    </div>
    <div class="w-full flex b-2 border-gray-200 text-xs">
      <div class="w-[calc(50%-1rem)] bg-slate-100 m-1 p-1 overflow-x-auto">
        <div class="w-full flex mb-1">
          commodity_id: <div :style="{ backgroundColor: commodityColor(data.commodity.commodity_id) }"
            class="h-full rounded-md px-2 flex ml-2">{{ data.commodity.commodity_id }}</div>
        </div>
        <div class="w-full flex">
          qty_tons: <div class="h-full rounded-md px-2 flex ml-2 bg-slate-300">{{ data.commodity.qty_tons }}</div>
        </div>
      </div>
      <div class="w-8 flex items-center justify-center">
        <Icon icon="nimbus:arrow-right" width="16" height="16" />
      </div>
      <div class="w-[calc(50%-1rem)] bg-slate-100 m-1 p-1 overflow-x-auto">
        <div class="w-full flex mb-1">
          vessel_id: <div :style="{ backgroundColor: typeColor(vesselID2Vessel[data.vessel.vessel_id].type) }"
            class="h-full rounded-md px-2 flex ml-2">{{ data.vessel.vessel_id }}</div>
        </div>
        <div class="w-full flex" v-if="vesselID2Vessel[data.vessel.vessel_id].tonnage">
          vessel_tonnage: <div class="h-full rounded-md px-2 flex ml-2 bg-slate-300">{{
        vesselID2Vessel[data.vessel.vessel_id].tonnage }}</div>
        </div>
      </div>
    </div>
  </div>
</template>