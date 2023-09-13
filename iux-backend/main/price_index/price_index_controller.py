from flask import Flask, request,jsonify, Blueprint
import pandas as pd
import os
from price_index.price_index_data_interface import reportgen 
import json
import gc
from price_index.price_index_agent import func_agent as agent

app = Flask(__name__)
price_index_blueprint = Blueprint('price_index', __name__)
@price_index_blueprint.route('/priceindex', methods=['POST'])  # changed to POST
def generate_report():
    input_json = request.get_json()
    input_json = json.loads(input_json)
    output_json = dict()
    result = reportgen(product_name = input_json['product-name'] if 'product-name' in input_json else None,
                       product_id = input_json['product-id'] if 'product-id' in input_json else None,
                       product_level = input_json['product-level'] if 'product-level' in input_json else None,
                       child_prod_level = input_json['child-prod-level'] if 'child-prod-level' in input_json else None,
                       product_agg = input_json['product-agg'] if 'product-agg' in input_json else 'N',
                       item_list = input_json['item-list'] if 'item-list' in input_json else None,
                       active = input_json['active'] if 'active' in input_json else 'Y',
                       group_name = input_json['group-name'] if 'group-name' in input_json else 'Y',
                       location_name = input_json['location-name'] if 'location-name' in input_json else None,
                       location_id = input_json['location-id'] if 'location-id' in input_json else None,
                       location_level = input_json['location-level'] if 'location-level' in input_json else None,
                       loc_agg = input_json['loc-agg'] if 'loc-agg' in input_json else 'N',
                       cal_year = input_json['cal-year'] if 'cal-year' in input_json else None,
                       quarter = input_json['quarter'] if 'quarter' in input_json else None,
                       period = input_json['period'] if 'period' in input_json else None,
                       week = input_json['week'] if 'week' in input_json else None,
                       day = input_json['day'] if 'day' in input_json else None,
                       start_date = input_json['start-date'] if 'start-date' in input_json else None,
                       end_date = input_json['end-date'] if 'end-date' in input_json else None,
                       calendar_id = input_json['calendar-id'] if 'calendar-id' in input_json else None,
                       cal_type = input_json['cal-type'] if 'cal-type' in input_json else 'Q',
                       user_id = input_json['user-id'] if 'user-id' in input_json else 'ejack',
                       cal_agg = input_json['cal-agg'] if 'cal-agg' in input_json else 'N',
                       pi_type = input_json['pi-type'] if 'pi-type' in input_json else 'S',
                       weighted_by = input_json['weighted-by'] if 'weighted-by' in input_json else None,
                       comp_city =input_json['comp-city'] if 'comp-city' in input_json else None,
                       comp_addr =input_json['comp-addr'] if 'comp-addr' in input_json else None,
                       comp_name = input_json['comp-name'] if 'comp-name' in input_json else None,
                       comp_tier = input_json['comp-tier'] if 'comp-tier' in input_json else None
                       ) 
    output_json['data'] = json.loads( result.replace('\\', '')) 
    
    return json.dumps(output_json) 

@price_index_blueprint.route('/priceindexllm', methods=['POST'])
def add_endpoint():
    data = request.get_json()
    
    print(data['prompt'])
    result = agent.run(data['prompt'])

    # with open('meta-data.json', 'r') as file:
    #     meta_data = json.load(file)

    final_res = {'summary': result }

    response_data = json.dumps({'result' : final_res})
    return response_data


if __name__ == '__main__':
    app.debug=True
    app.run( port = 9510, host = '0.0.0.0')