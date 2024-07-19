<script lang="ts" setup>
import { Icon } from '@iconify/vue'
import { storeToRefs } from 'pinia'
import { useStore } from '../stores/store'


const store = useStore()
const { remainVesselCommodityUnion, pairVesselCommodity } = storeToRefs(store)
</script>

<template>
    <div class="w-full h-full">
        <div class="w-full h-6 flex ml-2">
            <div class="w-8 h-full flex items-center justify-center">
                <Icon icon="clarity:connect-solid" width="32" height="32" />
            </div>
            <div class="">Match Vessel and Commodity</div>
            <div class="ml-auto flex items-center">
                <button class="icon-btn rounded w-8 h-full flex items-center justify-center b-2 border-gray-400"
                    @click="store.getDefaultPairVesselCommodity">
                    <Icon icon="fa6-solid:brain" />
                </button>
            </div>
        </div>
        <div class="w-full h-[calc(50%-0.75rem)] b-1 border-gray-200">
            <div class="w-full h-6 flex b-1 border-gray-200">
                <div class="w-8 h-full flex items-center justify-center">
                    <Icon icon="material-symbols:info" />
                </div>
                <div class="">Union</div>
            </div>
            <div class="w-full h-[calc(100%-1.5rem)] overflow-y-auto">
                <div v-for="data in remainVesselCommodityUnion" :key="data.date + data.location_id" :data="data"
                    class="w-full h-full">
                    <TheVesselCommodityUnionBox v-if="data.commoditys.length > 0 && data.vessels.length > 0"
                        :data="data" />
                </div>

            </div>
        </div>
            <div class="w-full h-[calc(50%-0.75rem)] overflow-y-auto b-1 border-gray-200">
                <div class="w-full h-6 flex b-1 border-gray-200">
                    <div class="w-8 h-full flex items-center justify-center">
                        <Icon icon="material-symbols:info" />
                    </div>
                    <div class="">Pair</div>
                </div>
                <div class="w-full h-[calc(100%-1.5rem)] overflow-y-auto">
                    <TheVesselCommodityPairBox v-for="data in pairVesselCommodity"
                        :key="data.vessel.movement_id + data.commodity.document_id" :data="data"
                        @deletePair="store.deleteVesselCommodityPair" />
                </div>
            </div>
        </div>
</template>