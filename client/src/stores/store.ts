/**
 * This pinia store demonstrate a way to load dynamic json resources from server.
 **/

import { defineStore } from 'pinia'
import * as d3 from 'd3'
import axios from 'axios'
import { get } from 'node_modules/axios/index.cjs'
import vesselMovements from '../data/vesselMovements.json'
import commodityDistributions from '../data/commodityDistributions.json'
import mc2 from '../data/mc2.json'
import pairVesselCommodity from '../data/pairVesselCommodity.json'
import vesselCommodityUnion from '../data/vesselCommodityUnion.json'
import transportMovements from '../data/transportMovements.json'
import harborMovements from '../data/harborMovements.json'
import Oceanus_Geography from '../data/Oceanus_Geography.json'
import locationCoordinates from '../data/locationCoordinates.json'

// import { get } from 'node_modules/axios/index.cjs'

const DATA_SERVER_URL = 'http://127.0.0.1:5000'

interface LocationCoordinates {
  [key: string]: [number, number]
}

interface VesselMovement {
  date: string
  vessel_id: string
  location_id: string
}

interface CommodityDistribution {
  date: string
  commodity_id: string
  location_id: string
  document_id: string
}

interface MovementSequence {
  [key: string]: [string, string][]
}
/**
 * The exampleData in client is a copy of the server,
 * we update the copy via the get method and modify the ontology via the post method
 */

export const useStore = defineStore({
  id: 'example',
  state: () => ({
    exampleData: [],
    vesselMovements: [] as any,
    commodityDistributions: commodityDistributions as CommodityDistribution[],
    locationCoordinates: locationCoordinates as any,
    vesselMovementsFlag: false,
    commodityDistributionsFlag: false,
    // dateInterval: ['2035-05-17', '2035-12-31'],
    dateInterval: ['2035-02-01', '2035-05-17'],
    vessels: (mc2 as any).nodes.filter((node: any) => node.type.includes('Entity.Vessel')) as [],
    locations: (mc2 as any).nodes.filter((node: any) => node.type.includes('Entity.Location')) as [],
    commodities: (mc2 as any).nodes.filter((node: any) => node.type.includes('Entity.Commodity')) as [],
    // selectedVesselIDs: ['dewie961', 'respectable717', 'malta8cc', 'snappersnatcher7be', 'largemouthbasslooterf95', 'freightfrontiers1bc', 'graylinggrabber802', 'whitesuckerwrangler0b3', 'roachrobberdb6'] as string[],
    selectedVesselIDs: (mc2 as any).nodes.filter((node: any) => node.type.includes('Entity.Vessel')).map((node: any) => node.id) as string[],
    selectedLocationIDs: (mc2 as any).nodes.filter((node: any) => node.type.includes('Entity.Location')).map((node: any) => node.id) as string[],
    selectedCommodityIDs: (mc2 as any).nodes.filter((node: any) => node.type.includes('Entity.Commodity')).map((node: any) => node.id) as string[],
    geoData: Oceanus_Geography as any,
    commoditys: [] as string[],
    commodityFishingLocations: {} as any,
    pairVesselCommodity: pairVesselCommodity as any,
    remainVesselCommodityUnion: vesselCommodityUnion as any,
    vesselCommodityUnion: vesselCommodityUnion as any,
    transportMovements: [] as any,
    harborMovements: [] as any,
    vesselTSNE: [] as any,
    focusVesselID: 'snappersnatcher7be',
    aggregateVesselMovements: [] as any,
  }),
  getters: {
    exampleDataLength(): number {
      return this.exampleData.length
    },
    vesselTypeColor(): any {
      // return (id: string) => {
      //   const color: any = {
      //     'Entity.Vessel.FishingVessel': '#E74C3C',
      //     'Entity.Vessel.CargoVessel': '#CF4436',
      //     'Entity.Vessel.Tour': '#B93E30',
      //     'Entity.Vessel.Other': '#A4382A',
      //     'Entity.Vessel.Research': '#8F3224',
      //     'Entity.Vessel.Ferry.Passenger': '#7A2C1E',
      //     'Entity.Vessel.Ferry.Cargo': '#652618',
      //   }
      //   return color[id]
      // }
      return d3.scaleOrdinal(d3.schemeCategory10).domain(this.vesselTypes)
    },
    locationColor(): any {
      // return (id: string) => {
      //   const color: any = {
      //     'City of Haacklee': '#4A90E2',
      //     'City of Lomark': '#5BA1F2',
      //     'City of Himark': '#6CB2FF',
      //     'City of Paackland': '#7CBDF1',
      //     'City of South Paackland': '#8CC8EA',
      //     'City of Port Grove': '#9CD3E4',
      //     'Exit West': '#3FA36C',
      //     'Exit East': '#50AE7C',
      //     'Exit South': '#61B98C',
      //     'Exit North': '#72C49C',
      //     'Nav 1': '#83CFAC',
      //     'Nav 2': '#94DABC',
      //     'Nav 3': '#A5E5CC',
      //     'Nav A': '#39A058',
      //     'Nav B': '#2F8E4E',
      //     'Nav C': '#278C44',
      //     'Nav D': '#1F843C',
      //     'Nav E': '#177C34',
      //     'Cod Table': '#F9E076',
      //     'Wrasse Beds': '#F9D460',
      //     'Tuna Shelf': '#F9C84A',
      //     'Ghoti Preserve': '#BC77DB',
      //     'Nemo Reef': '#A864C9',
      //     'Don Limpet Preserve': '#943DB7',
      //   }
      //   return color[id]
      // }
      return d3.scaleOrdinal(d3.schemeSet3.concat(d3.schemeTableau10, d3.schemePastel1)).domain(this.locationIDs)
    },
    commodityColor(): any {
      // return (id: string) => {
      //   const color: any = {
      //     'gadusnspecificatae4ba': '#FF7F50',
      //     'piscesfrigus900': '#FF8C60',
      //     'piscesfoetidaae7': '#FF9970',
      //     'labridaenrefert9be': '#FFA680',
      //     'habeaspisces4eb': '#FFB390',
      //     'piscissapidum9b7': '#FFC0A0',
      //     'thunnininveradb7': '#FFCDAA',
      //     'piscisosseusb6d': '#FFDAC4',
      //     'oncorhynchusrosea790': '#FFE7DE',
      //     'piscessatisb87': '#FFF4E8',
      //   }
      //   return color[id]
      // }
      return d3.scaleOrdinal(d3.schemeSet1).domain(this.commodityIDs)
    },
    locationIDs(): string[] {
      return [...new Set(this.locations.map((location: any) => location.id))]
    },
    vesselIDs(): string[] {
      return [...new Set(this.vessels.map((vessel: any) => vessel.id))]
    },
    vesselTypes(): string[] {
      return [...new Set(this.vessels.map((vessel: any) => vessel.type))]
    },
    commodityIDs(): string[] {
      return [...new Set(this.commodities.map((commodity: any) => commodity.id))]
    },
    vesselID2Vessel(): { [key: string]: any } {
      const vesselID2Vessel: { [key: string]: any } = {}
      this.vessels.forEach((vessel: any) => {
        vesselID2Vessel[vessel.id] = vessel
      })
      return vesselID2Vessel
    },
    locationID2Location(): { [key: string]: any } {
      const locationID2Location: { [key: string]: any } = {}
      this.locations.forEach((location: any) => {
        locationID2Location[location.id] = location
      })
      return locationID2Location
    },
    commodityID2Commodity(): { [key: string]: any } {
      const commodityID2Commodity: { [key: string]: any } = {}
      this.commodities.forEach((commodity: any) => {
        commodityID2Commodity[commodity.id] = commodity
      })
      return commodityID2Commodity
    },
    vesselID2Name(): { [key: string]: string } {
      const vesselID2VesselName: { [key: string]: string } = {}
      this.vessels.forEach((vessel: any) => {
        vesselID2VesselName[vessel.id] = vessel.Name
      })
      return vesselID2VesselName
    },
    locationID2Name(): { [key: string]: string } {
      const locationID2LocationName: { [key: string]: string } = {}
      this.locations.forEach((location: any) => {
        locationID2LocationName[location.id] = location.Name
      })
      return locationID2LocationName
    },
    commodityID2Name(): { [key: string]: string } {
      const commodityID2CommodityName: { [key: string]: string } = {}
      this.commodities.forEach((commodity: any) => {
        commodityID2CommodityName[commodity.id] = commodity.name
      })
      return commodityID2CommodityName
    },
    vesselMovementSequences() {
      const vesselMovementSequences: MovementSequence = {}

      this.vesselMovements.forEach((record) => {
        const { vessel_id, date, location_id } = record

        if (!vesselMovementSequences[vessel_id])
          vesselMovementSequences[vessel_id] = []
        vesselMovementSequences[vessel_id].push([date, location_id])
      })

      Object.keys(vesselMovementSequences).forEach((vesselId) => {
        vesselMovementSequences[vesselId].sort((a, b) => new Date(a[0]).getTime() - new Date(b[0]).getTime())
      })

      return vesselMovementSequences
    },
    frequencyCommodityLocations() {
      const frequencyDict: any = {}
      // 计算每个商品在每个地点出现的次数
      for (const distribution of this.commodityDistributions) {
        const { commodity_id, location_id } = distribution
        if (!frequencyDict[commodity_id])
          frequencyDict[commodity_id] = {}
        if (!frequencyDict[commodity_id][location_id])
          frequencyDict[commodity_id][location_id] = 0
        frequencyDict[commodity_id][location_id] += 1
      }

      // 转换为所需的数组格式
      const frequencyArray = []
      for (const commodity_id in frequencyDict) {
        for (const location_id in frequencyDict[commodity_id]) {
          frequencyArray.push({
            commodity_id,
            location_id,
            frequency: frequencyDict[commodity_id][location_id],
          })
        }
      }

      return frequencyArray
    },
    frequencyVesselLocations() {
      const frequencyDict: any = {}
      // 计算每个船只在每个地点出现的次数
      for (const movement of this.vesselMovements) {
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
    },
    frequencyCommodityVessels() {
      const frequencyDict: { [key: string]: { [key: string]: number } } = {}

      // 创建一个查找表，方便快速检查特定日期和地点的商品出现情况
      const commodityLookup: { [key: string]: { [key: string]: string[] } } = {}

      for (const distribution of this.commodityDistributions) {
        const date = new Date(distribution.date).toISOString().split('T')[0]
        const locationId = distribution.location_id

        if (!commodityLookup[date])
          commodityLookup[date] = {}

        if (!commodityLookup[date][locationId])
          commodityLookup[date][locationId] = []

        commodityLookup[date][locationId].push(distribution.commodity_id)
      }

      // 遍历VesselMovement列表，检查相同日期和地点是否存在对应的商品
      for (const movement of this.vesselMovements) {
        const date = new Date(movement.date).toISOString().split('T')[0]
        const locationId = movement.location_id

        if (commodityLookup[date] && commodityLookup[date][locationId]) {
          for (const commodityId of commodityLookup[date][locationId]) {
            const key = `${commodityId}-${movement.vessel_id}`
            if (!frequencyDict[key])
              frequencyDict[key] = {}
            if (!frequencyDict[key][locationId])
              frequencyDict[key][locationId] = 0
            frequencyDict[key][locationId] += 1
          }
        }
      }

      // 将频率计数转换为数组格式
      const frequencyArray = []
      for (const key in frequencyDict) {
        const [commodity_id, vessel_id] = key.split('-')
        for (const location_id in frequencyDict[key]) {
          frequencyArray.push({
            commodity_id,
            vessel_id,
            location_id,
            frequency: frequencyDict[key][location_id],
          })
        }
      }
      return frequencyArray
    },
  },
  actions: {
    // generic HTTP GET request
    get(api: string, callback: Function) {
      axios.get(`${DATA_SERVER_URL}/${api}`).then(
        (response) => {
          callback(response.data)
        },
        (errResponse) => {
          console.error(errResponse)
        },
      )
    },
    // generic HTTP POST request
    post(api: string, param: object, callback: Function) {
      axios.post(`${DATA_SERVER_URL}/${api}`, param).then(
        (response) => {
          callback(response.data)
        },
        (errResponse) => {
          console.error(errResponse)
        },
      )
    },
    // the async and await version if you do not use generic requests
    async get_example_data_async() {
      try {
        const response = await axios.get(`${DATA_SERVER_URL}/get_example_data`)
        this.exampleData = response.data
      }
      catch (error) {
        console.error(error)
        // display a user-friendly error message on the UI
      }
    },
    modify_example_data() {
      this.post('modify_example_data', { example: 100 }, (data: []) => {
        this.exampleData = data
      })
    },
    async getVesselMovements() {
      await new Promise(resolve => setTimeout(resolve, 1000))
      this.vesselMovements = transportMovements
      this.transportMovements = transportMovements
      this.harborMovements = harborMovements
    },
    getDefaultPairVesselCommodity() {
      this.pairVesselCommodity = pairVesselCommodity
      this.remainVesselCommodityUnion = []
    },
    deleteVesselCommodityPair(pair: any) {
      this.pairVesselCommodity = this.pairVesselCommodity.filter((item: any) => item !== pair)
      const union = this.remainVesselCommodityUnion.filter((item: any) => item.date === pair.date && item.location_id === pair.location_id)[0]
      union.vessels.push(pair.vessel)
      union.commoditys.push(pair.commodity)
    },
    addVesselCommodityPair(date: string, location_id: string, vessel: any, commodity: any) {
      this.pairVesselCommodity.unshift({ date, location_id, vessel, commodity })
      const union = this.remainVesselCommodityUnion.filter((item: any) => item.date === date && item.location_id === location_id)[0]
      union.vessels = union.vessels.filter((item: any) => item !== vessel)
      union.commoditys = union.commoditys.filter((item: any) => item !== commodity)
    },
    initialization() {
      this.selectedVesselIDs = this.vessels.map((vessel: any) => vessel.id)
      this.selectedLocationIDs = this.locations.map((location: any) => location.id)
      this.selectedCommodityIDs = this.commodities.map((commodity: any) => commodity.id)
      this.dateInterval = ['2035-02-01', '2035-12-31']
    },
    getVesselTSNE() {
      this.post('get_vessel_tsne', { start_date: this.dateInterval[0], end_date: this.dateInterval[1], vessel_ids: this.vesselIDs, location_ids: this.selectedLocationIDs }, (data: []) => {
        this.vesselTSNE = data
      })
    },
    getAggregatedVesselMovements() {
      this.post('get_aggregate_vessel_movements', { start_date: this.dateInterval[0], end_date: this.dateInterval[1], vessel_ids: this.selectedVesselIDs, location_ids: this.selectedLocationIDs }, (data: []) => {
        this.aggregateVesselMovements = data
      })
    },
    getVesselTypeColor() {
      return (id: string) => {
        const color: any = {
          'Entity.Vessel.FishingVessel': '#E74C3C',
          'Entity.Vessel.CargoVessel': '#CF4436',
          'Entity.Vessel.Tour': '#B93E30',
          'Entity.Vessel.Other': '#A4382A',
          'Entity.Vessel.Research': '#8F3224',
          'Entity.Vessel.Ferry.Passenger': '#7A2C1E',
          'Entity.Vessel.Ferry.Cargo': '#652618',
        }
        return color[id]
      }
    },
    getLocationColor(id: string) {
      return (id: string) => {
        const color: any = {
          'City of Haacklee': '#4A90E2',
          'City of Lomark': '#5BA1F2',
          'City of Himark': '#6CB2FF',
          'City of Paackland': '#7CBDF1',
          'City of South Paackland': '#8CC8EA',
          'City of Port Grove': '#9CD3E4',
          'Exit West': '#3FA36C',
          'Exit East': '#50AE7C',
          'Exit South': '#61B98C',
          'Exit North': '#72C49C',
          'Nav 1': '#83CFAC',
          'Nav 2': '#94DABC',
          'Nav 3': '#A5E5CC',
          'Nav A': '#39A058',
          'Nav B': '#2F8E4E',
          'Nav C': '#278C44',
          'Nav D': '#1F843C',
          'Nav E': '#177C34',
          'Cod Table': '#F9E076',
          'Wrasse Beds': '#F9D460',
          'Tuna Shelf': '#F9C84A',
          'Ghoti Preserve': '#BC77DB',
          'Nemo Reef': '#A864C9',
          'Don Limpet Preserve': '#943DB7',
        }
        return color[id]
      }
    },
    getCommodityColor(id: string) {
      return (id: string) => {
        const color: any = {
          'gadusnspecificatae4ba': '#FF7F50',
          'piscesfrigus900': '#FF8C60',
          'piscesfoetidaae7': '#FF9970',
          'labridaenrefert9be': '#FFA680',
          'habeaspisces4eb': '#FFB390',
          'piscissapidum9b7': '#FFC0A0',
          'thunnininveradb7': '#FFCDAA',
          'piscisosseusb6d': '#FFDAC4',
          'oncorhynchusrosea790': '#FFE7DE',
          'piscessatisb87': '#FFF4E8',
        }
        return color[id]
      }
    },
  },
})
