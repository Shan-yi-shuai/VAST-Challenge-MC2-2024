import os
import json
from syslog import syslog
import pandas as pd
import json
from datetime import datetime, timedelta
from collections import Counter
from collections import defaultdict
import numpy as np
from sklearn.manifold import TSNE
from tslearn.metrics import cdist_dtw
from tslearn.preprocessing import TimeSeriesScalerMeanVariance

PATH_DATA_FOLDER = './data/'
FILE_MC2_JSON = 'mc2.json'
FILE_OCEANUS_GEOGRAPHY_NODES_JSON = 'Oceanus_Geography_Nodes.json'
FILE_OCEANUS_GEOGRAPHY_GEOJSON = 'Oceanus_Geography.geojson'
FILE_LOCATION_COORDINATES = 'location_coordinates.json'
FILE_TRANSPORT_MOVEMENTS = 'transportMovements.json'

ENTITY_TYPES = {
    'document': {'delivery_report': 'Entity.Document.DeliveryReport'},
    'vessel': {'fishing_vessel': 'Entity.Vessel.FishingVessel',
               'cargo_vessel': 'Entity.Vessel.CargoVessel',
               'tour_vessel': 'Entity.Vessel.Tour',
               'other_vessel': 'Entity.Vessel.Other',
               'research_vessel': 'Entity.Vessel.Research',
               'ferry_vessel': {'passenger_vessel': 'Entity.Vessel.Ferry.Passenger',
                                 'cargo_vessel': 'Entity.Vessel.Ferry.Cargo'}
               },
    'location': {'point': 'Entity.Location.Point',
                 'city': 'Entity.Location.City',
                 'region': 'Entity.Location.Region',
                 },
    'commodity': {'fish': 'Entity.Commodity.Fish'}
}

EVENT_TYPES = {
    'transport_event': 'Event.TransportEvent.TransponderPing',
    'transaction': 'Event.Transaction',
    'harbor_report': 'Event.HarborReport',
}


class Model:
    def __init__(self):
        self.DATA_FOLDER = PATH_DATA_FOLDER

        try:
            with open(os.path.join(self.DATA_FOLDER, FILE_MC2_JSON), 'r') as file:
                mc2 = json.load(file)
                self.entities = mc2['nodes']
                self.events = mc2['links']
        except Exception as e:
            print(f'could not open: {FILE_MC2_JSON} because {e}')
            
        try:
            with open(os.path.join(self.DATA_FOLDER, FILE_TRANSPORT_MOVEMENTS), 'r') as file:
                self.transport_movement_start_end = json.load(file)
        except Exception as e:
            print(f'could not open: {FILE_MC2_JSON} because {e}')
        
        self.transport_movements = self.get_transport_movements()


    def get_events(self, event_type):
        return pd.DataFrame([event for event in self.events if event['type'] == event_type])

    def get_entities(self, entity_type):
        return pd.DataFrame([entity for entity in self.entities if entity['type'] == entity_type])

    def get_entities_vague(self, entity_type):
        return pd.DataFrame([entity for entity in self.entities if entity['type'].startswith(entity_type)])

    def get_entity(self, entity_id):
        return pd.DataFrame([entity for entity in self.entities if entity['id'] == entity_id])

    def get_location_coordinates(self):
        return self.location_coordinates

    def get_geo_data(self):
        return self.oceanus_geography_geojson

    def get_commodity_fishing_locations(self):
        df_location_region = pd.DataFrame(
            self.get_entities(ENTITY_TYPES['location']['region']))
        df_commodities = pd.DataFrame(
            self.get_entities(ENTITY_TYPES['commodity']['fish']))

        commodity_fishing_locations = {}

        for _, row in df_commodities.iterrows():
            commodity_name = row['name']
            commodity_id = row['id']
            commodity_fishing_locations[commodity_id] = []
            for _, location_row in df_location_region.iterrows():
                fish_species_present = location_row['fish_species_present']
                if commodity_name in fish_species_present:
                    commodity_fishing_locations[commodity_id].append(
                        location_row['id'])

        return commodity_fishing_locations

    def get_transport_movements(self):
        self.transport_movements = []
        df_transport_events = pd.DataFrame(
            self.get_events(EVENT_TYPES['transport_event']))

        if not df_transport_events.empty:
            # 尝试第一种格式解析日期时间
            df_transport_events['start_time'] = pd.to_datetime(
                df_transport_events['time'], errors='coerce', format="%Y-%m-%dT%H:%M:%S.%f")
            # 对于解析失败的，使用第二种格式
            mask = df_transport_events['start_time'].isna()
            df_transport_events.loc[mask, 'start_time'] = pd.to_datetime(
                df_transport_events.loc[mask, 'time'], format="%Y-%m-%dT%H:%M:%S")

            df_transport_events['end_time'] = df_transport_events['start_time'] + \
                pd.to_timedelta(df_transport_events['dwell'], unit='s')

            # 将数据按天拆分
            for _, row in df_transport_events.iterrows():
                location_id = row['source']
                vessel_id = row['target']
                start_time = row['start_time']
                end_time = row['end_time']

                current_date = start_time
                while current_date.date() <= end_time.date():
                    if current_date.date() == start_time.date():
                        if current_date.date() == end_time.date():
                            dwell = (end_time - start_time).total_seconds()
                        else:
                            dwell = (datetime.combine(current_date.date(), datetime.max.time()) - start_time).total_seconds()
                    elif current_date.date() == end_time.date():
                        dwell = (end_time - datetime.combine(current_date.date(), datetime.min.time())).total_seconds()
                    else:
                        dwell = 24 * 3600  # Full day in seconds

                    self.transport_movements.append({
                        'date': current_date.strftime("%Y-%m-%d"),
                        'location_id': location_id,
                        'vessel_id': vessel_id,
                        # 'vessel_type': self.get_entity(vessel_id)['type'].values[0],
                        'type': 'transport',
                        # 'movement_id': vessel_id + '_' + location_id + '_' + current_date.strftime("%Y-%m-%dT%H:%M:%S"),
                        # 'key': vessel_id + '_' + location_id + '_' + current_date.strftime("%Y-%m-%dT%H:%M:%S"),
                        'dwell': dwell
                    })
                    current_date += timedelta(days=1)
        # self.transport_movements.sort(
        #     key=lambda x: datetime.strptime(x['date'], "%Y-%m-%dT%H:%M:%S"))
        return self.transport_movements

    def get_harbor_movements(self):
        self.harbor_movements = []
        df_harbor_reports = pd.DataFrame(
            self.get_events(EVENT_TYPES['harbor_report']))
        if not df_harbor_reports.empty:
            df_harbor_reports['date'] = pd.to_datetime(
                df_harbor_reports['date'], format="%Y-%m-%d")

            for _, row in df_harbor_reports.iterrows():
                location_id = row['target']
                vessel_id = row['source']
                date = row['date']

                self.harbor_movements.append({
                    'date': date.strftime("%Y-%m-%dT%H:%M:%S"),
                    'location_id': location_id,
                    'vessel_id': vessel_id,
                    'vessel_type': self.get_entity(vessel_id)['type'].values[0],
                    'type': 'harbor',
                    'movement_id': vessel_id + '_' + location_id + '_' + date.strftime("%Y-%m-%dT%H:%M:%S"),
                    'key': vessel_id + '_' + location_id + '_' + date.strftime("%Y-%m-%dT%H:%M:%S"),
                })
        self.harbor_movements.sort(
            key=lambda x: datetime.strptime(x['date'], "%Y-%m-%dT%H:%M:%S"))
        return self.harbor_movements

    def get_commodity_distributions(self):
        self.commodity_distributions = []

        # 获取交易事件数据框
        df_transactions = pd.DataFrame(
            self.get_events(EVENT_TYPES['transaction']))

        if not df_transactions.empty:
            # 将日期转换为日期对象，并格式化为字符串
            df_transactions['date'] = pd.to_datetime(
                df_transactions['date'], format="%Y-%m-%d").dt.strftime("%Y-%m-%d")

            # 使用 groupby 和 apply 来处理每个 document_id 的数据
            def process_group(group):
                date = group['date'].values[0]
                commodity_id = group['target'].values[0]
                location_id = group['target'].values[1] if len(
                    group) > 1 else None
                return {'date': date, 'commodity_id': commodity_id, 'location_id': location_id, 'document_id': group['source'].values[0]}

            self.commodity_distributions = df_transactions.groupby(
                'source').apply(process_group).tolist()

        print(len(self.commodity_distributions))
        return self.commodity_distributions

    def get_vessel_movement_sequences(self, vessel_movements):
        vessel_movement_sequences = {}
        for record in vessel_movements:
            vessel_id = record['vessel_id']
            date = record['date']
            location_id = record['location_id']
            if vessel_id not in vessel_movement_sequences:
                vessel_movement_sequences[vessel_id] = []
            vessel_movement_sequences[vessel_id].append((date, location_id))
        for vessel_id, movements in vessel_movement_sequences.items():
            movements.sort(key=lambda x: x[0])
        return vessel_movement_sequences

    def get_date_location_commodity(self):
        df_transaction = self.get_events(EVENT_TYPES['transaction'])
        df_document = self.get_entities(
            ENTITY_TYPES['document']['delivery_report'])
        documents = df_transaction['source'].unique()
        self.date_location_commodity = []
        for document in documents:
            pair = df_transaction[df_transaction['source'] == document]
            date = pair['date'].values[0]
            date = datetime.strptime(date, '%Y-%m-%d')
            commodity = pair['target'].values[0]
            location = pair['target'].values[1]
            qty_tons = df_document[df_document['id']
                                   == document]['qty_tons'].values[0]
            self.date_location_commodity.append({'date': date.strftime(
                "%Y-%m-%d"), 'commodity_id': commodity, 'location_id': location, 'qty_tons': qty_tons, 'document_id': document})
        return self.date_location_commodity

    def get_date_location_commodity_export(self):
        df_transaction = self.get_events(EVENT_TYPES['transaction'])
        df_document = self.get_entities(
            ENTITY_TYPES['document']['delivery_report'])
        documents = df_transaction['source'].unique()
        self.date_location_commodity = []
        for document in documents:
            pair = df_transaction[df_transaction['source'] == document]
            date = pair['date'].values[0]
            date = datetime.strptime(date, '%Y-%m-%d')
            commodity = pair['target'].values[0]
            location = pair['target'].values[1]
            qty_tons = df_document[df_document['id']
                                   == document]['qty_tons'].values[0]
            if qty_tons > 0:
                continue
            self.date_location_commodity.append({'date': date.strftime(
                "%Y-%m-%d"), 'commodity_id': commodity, 'location_id': location, 'qty_tons': qty_tons, 'document_id': document})
        return self.date_location_commodity

    def get_date_location_commodity_import(self):
        df_transaction = self.get_events(EVENT_TYPES['transaction'])
        df_document = self.get_entities(
            ENTITY_TYPES['document']['delivery_report'])
        documents = df_transaction['source'].unique()
        self.date_location_commodity = []
        for document in documents:
            pair = df_transaction[df_transaction['source'] == document]
            date = pair['date'].values[0]
            date = datetime.strptime(date, '%Y-%m-%d')
            commodity = pair['target'].values[0]
            location = pair['target'].values[1]
            qty_tons = df_document[df_document['id']
                                   == document]['qty_tons'].values[0]
            if qty_tons <= 0:
                continue
            self.date_location_commodity.append({'date': date.strftime(
                "%Y-%m-%d"), 'commodity_id': commodity, 'location_id': location, 'qty_tons': qty_tons, 'document_id': document})
        return self.date_location_commodity

    def get_vessel_commodity_union(self, vessel_movements, date_location_commodity):
        date_loc_commodity_qty = {}
        for item in date_location_commodity:
            # if item['location'] not in location_list:
            #     # print(item)
            #     continue
            key = (datetime.strptime(
                item['date'], '%Y-%m-%d').date(), item['location_id'])
            if key not in date_loc_commodity_qty:
                date_loc_commodity_qty[key] = []
            date_loc_commodity_qty[key].append(
                {'document_id': item['document_id'], 'commodity_id': item['commodity_id'], 'qty_tons': item['qty_tons']})

        date_loc_vessel = {}
        for item in vessel_movements:
            key = (datetime.strptime(
                item['date'], '%Y-%m-%dT%H:%M:%S').date(), item['location_id'])
            if key not in date_loc_vessel:
                date_loc_vessel[key] = []
            date_loc_vessel[key].append(
                {'movement_id': item['movement_id'], 'vessel_id': item['vessel_id'], 'key': item['key']})
        date_loc_vessel_commodity = []
        all_keys = set(set(date_loc_commodity_qty.keys()).union(
            set(date_loc_vessel.keys())))

        for key in all_keys:
            date, location = key
            # assert location in location_list, key
            commoditys = date_loc_commodity_qty.get(key, [])
            vessels = date_loc_vessel.get(key, [])
            # if len(commoditys) == 0 or len(vessels) == 0:
            #     continue
            date_loc_vessel_commodity.append({'date': date.strftime(
                '%Y-%m-%d'), 'location_id': location, 'commoditys': commoditys, 'vessels': vessels})
        return sorted(date_loc_vessel_commodity, key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"))

    def refresh_unions(self, original_union, vessel_movements):
        date_loc_vessel = {}
        for item in vessel_movements:
            key = (datetime.strptime(
                item['date'], '%Y-%m-%dT%H:%M:%S').date(), item['location_id'])
            if key not in date_loc_vessel:
                date_loc_vessel[key] = []
            date_loc_vessel[key].append(
                {'movement_id': item['movement_id'], 'vessel_id': item['vessel_id'], 'key': item['key']})

        for key in date_loc_vessel.keys():
            date, location = key
            for item in original_union:
                if item['date'] == date.strftime('%Y-%m-%d') and item['location_id'] == location:
                    item['vessels'] = item['vessels'] + date_loc_vessel[key]
        return original_union
    
    def get_vessel_time_series(self, start_date, end_date, vessel_ids, location_ids):
        location_indices = {location: index for index, location in enumerate(location_ids)}
        # 生成日期列表
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        date_list = [(start + timedelta(days=x)).strftime("%Y-%m-%d") for x in range((end - start).days + 1)]
        filtered_movements = [record for record in self.transport_movements if record['vessel_id'] in vessel_ids and record['date'] in date_list and record['location_id'] in location_ids and datetime.strptime(record['date'], "%Y-%m-%d") >= start and datetime.strptime(record['date'], "%Y-%m-%d") <= end]
        result_count = defaultdict(lambda: defaultdict(lambda: [0] * len(location_ids)))
        result_dwell = defaultdict(lambda: defaultdict(lambda: [0] * len(location_ids)))
        
        for record in filtered_movements:
            vessel_id = record['vessel_id']
            date = record['date']
            location_id = record['location_id']
            dwell = record['dwell']
            
            # 增加对应位置的停留时间
            result_dwell[vessel_id][date][location_indices[location_id]] += dwell
            
            # 增加对应位置的计数
            result_count[vessel_id][date][location_indices[location_id]] += 1

        final_result = {}
        for vessel in result_count.keys():
            final_result[vessel] = []
            for date in date_list:
                counts = result_count[vessel][date]
                dwells = result_dwell[vessel][date]
                combined = [(count, dwell) for count, dwell in zip(counts, dwells)]
                final_result[vessel].append([date, combined])
            
        return final_result

    def get_vessel_tsne(self, final_result):
        # 提取时间序列数据
        time_series_data = []
        vessels = []

        for vessel, data in final_result.items():
            time_series = [entry[1] for entry in data]
            time_series_data.append(time_series)
            vessels.append(vessel)
        # 转换为 numpy 数组并标准化
        time_series_data = np.array(time_series_data)
        # 展开二维数据并进行标准化
        n_samples, n_timesteps, n_locations, n_features = time_series_data.shape
        time_series_data = time_series_data.reshape(n_samples, n_timesteps, n_locations * n_features)
        time_series_data = TimeSeriesScalerMeanVariance().fit_transform(time_series_data)

        # 计算时间序列之间的 TW 距离矩阵
        dtw_distances = cdist_dtw(time_series_data)
        tsne = TSNE(n_components=2, perplexity=50, random_state=0)
        transformed_data = tsne.fit_transform(dtw_distances)
        transformed_data = transformed_data.astype(float).tolist()
        return json.dumps([[vessel, coord] for vessel, coord in zip(vessels, transformed_data)])
    
    def get_aggregate_vessel_movements(self, start_date, end_date, vessel_ids, location_ids):
        # 将start_date和end_date转换为datetime对象
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # 创建DataFrame
        df = pd.DataFrame(self.transport_movement_start_end)
        
        # 转换时间列为datetime格式
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['end_time'] = pd.to_datetime(df['end_time'])
        
        # 筛选符合时间范围、船只ID和位置ID的数据
        filtered_df = df[
            (df['start_time'] <= end) & 
            (df['end_time'] >= start) & 
            (df['vessel_id'].isin(vessel_ids)) & 
            (df['location_id'].isin(location_ids))
        ]
        
        # 获取所有时间点
        time_points = pd.concat([filtered_df['start_time'], filtered_df['end_time']]).drop_duplicates().sort_values().reset_index(drop=True)
        time_points = time_points[time_points <= end]
        if time_points.iloc[-1] != end:
            time_points = pd.concat([time_points, pd.Series([end])]).drop_duplicates().sort_values().reset_index(drop=True)
            
        time_points = time_points[time_points >= start]
        if time_points.iloc[0] != start:
            time_points = pd.concat([pd.Series([start]), time_points]).drop_duplicates().sort_values().reset_index(drop=True)

        
        
        aggregated_results = []
        
        for i in range(len(time_points) - 1):
            start_interval = time_points[i]
            end_interval = time_points[i + 1]
            
            # 过滤在当前时间区间内的记录
            mask = (filtered_df['start_time'] < end_interval) & (filtered_df['end_time'] > start_interval)
            current_interval = filtered_df[mask]
            
            # 计算位置出现次数
            location_count = current_interval['location_id'].value_counts()
            
            if not location_count.empty:
                max_location = location_count.idxmax()
            else:
                max_location = None
            
            # 合并连续相同的location_id
            if aggregated_results and aggregated_results[-1]['location_id'] == max_location:
                aggregated_results[-1]['end_time'] = end_interval.isoformat()
            else:
                aggregated_results.append({
                    'start_time': start_interval.isoformat(),
                    'end_time': end_interval.isoformat(),
                    'location_id': max_location,
                    'vessel_id': 'aggregation'
                })
        
        return json.dumps(aggregated_results)
    
    """
    to_json is frequently used in outputing pandas DataFrame
    The 'records' and 'index' orients are typically helpful in rendering front-end components.
    force_ascii is set to False to support diverse character sets.
    """
    # The following methods all target netflix dataset

    def get_example_data(self):
        return json.dumps(self.json_data, ensure_ascii=False)
        # return self.json_data.to_json(orient='records', force_ascii=False)

    def modify_example_data(self, value):
        # modify the data
        self.json_data = value
        return json.dumps(self.json_data, ensure_ascii=False)
