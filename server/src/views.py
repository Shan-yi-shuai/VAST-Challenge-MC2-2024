from src import app
from src.models import Model
from flask import request
import json

# initialize the model
model = Model()
print("================================================================")


@app.route('/get')
def _get():
    return "Get"


@app.route('/get_example_data')
def _get_example_data():
    return model.get_example_data()


@app.route('/modify_example_data', methods=['POST'])
def _modify_example_data():
    post_data = request.data.decode()
    post_data = json.loads(post_data)
    value = post_data["example"]
    if not isinstance(value, (int)):
        return ""
    model.modify_example_data(value)
    return model.get_example_data()


@app.route('/get_vessel_movements')
def get_vessel_movements():
    return model.get_vessel_movements()


@app.route('/get_vessel_tsne', methods=['POST'])
def get_vessel_tsne():
    post_data = request.data.decode()
    post_data = json.loads(post_data)
    start_date = post_data["start_date"]
    end_date = post_data["end_date"]
    vessel_ids = post_data["vessel_ids"]
    location_ids = post_data["location_ids"]
    time_series = model.get_vessel_time_series(start_date, end_date, vessel_ids, location_ids)
    return model.get_vessel_tsne(time_series)

@app.route('/get_aggregate_vessel_movements', methods=['POST'])
def get_aggregate_vessel_movements():
    post_data = request.data.decode()
    post_data = json.loads(post_data)
    start_date = post_data["start_date"]
    end_date = post_data["end_date"]
    vessel_ids = post_data["vessel_ids"]
    location_ids = post_data["location_ids"]
    
    return model.get_aggregate_vessel_movements(start_date, end_date, vessel_ids, location_ids)