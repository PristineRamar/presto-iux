# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 14:34:19 2023

@author: Ashutosh
"""

from flask import Flask, request, jsonify
import json
import gc
import pandas as pd

from affinity_data_interface import cost_api, price_api, promotion_api, movement_api, hier_api,affinity_api
#from dummy_data_interface import cost_api, price_api, promotion_api, movement_api, hier_api
from datetime import datetime
 
app = Flask(__name__)  
  

     
#     input_json = request.get_json()
#     output_json = dict()
    
#     with open('log.txt', 'a') as logfile:        
#         logfile.write(pd.to_datetime(datetime.now()).strftime('%Y-%m-%d %I:%M:%S %p') + '\n')
#         logfile.write('    API: Movement\n')
#         logfile.write('    Args: ' + json.dumps(input_json) + '\n\n')
     
#     try:
#         response = movement_api(product_name = input_json['product-name'] if 'product-name' in input_json else None,
#                                 product_id = input_json['product-id'] if 'product-id' in input_json else None,
#                                 product_level = input_json['product-level'] if 'product-level' in input_json else None,
#                                 item_list = input_json['item-list'] if 'item-list' in input_json else None,
#                                 active = input_json['active'] if 'active' in input_json else 'Y',
#                                 location_name = input_json['location-name'] if 'location-name' in input_json else None,
#                                 location_id = input_json['location-id'] if 'location-id' in input_json else None,
#                                 location_level = input_json['location-level'] if 'location-level' in input_json else None,
#                                 cal_year = input_json['cal-year'] if 'cal-year' in input_json else None,
#                                 quarter = input_json['quarter'] if 'quarter' in input_json else None,
#                                 period = input_json['period'] if 'period' in input_json else None,
#                                 week = input_json['week'] if 'week' in input_json else None,
#                                 day = input_json['day'] if 'day' in input_json else None,
#                                 start_date = input_json['start-date'] if 'start-date' in input_json else None,
#                                 end_date = input_json['end-date'] if 'end-date' in input_json else None,
#                                 calendar_id = input_json['calendar-id'] if 'calendar-id' in input_json else None,
#                                 cal_type = input_json['cal-type'] if 'cal-type' in input_json else None,
#                                 promoted = input_json['promoted'] if 'promoted' in input_json else 'All',
#                                 user_id = input_json['user-id'])
        
#         output_json['timeframe'] = response[3]
#         output_json['locations'] = response[2]
#         output_json['products'] = response[1]
#         output_json['data'] = json.loads(response[0].to_json(orient = 'records').replace('\\', ''))           
        
#     except:
#         output_json['error-message'] = 'Could not process request.'
#     return json.dumps(output_json)




    
    
    
    
     
    input_json = request.get_json()
    output_json = dict()
    
    with open('log.txt', 'a') as logfile:        
        logfile.write(pd.to_datetime(datetime.now()).strftime('%Y-%m-%d %I:%M:%S %p') + '\n')
        logfile.write('    API: Hierarchy\n')
        logfile.write('    Args: ' + json.dumps(input_json) + '\n\n')
     
    try:
        response = hier_api(product_name = input_json['product-name'] if 'product-name' in input_json else None,
                            product_id = input_json['product-id'] if 'product-id' in input_json else None,
                            product_level = input_json['product-level'] if 'product-level' in input_json else None,
                            detail_level = 1,
                            other_levels = [5, 4, 3, 2, 1.5, 1])

        output_json['data'] = json.loads(response.to_json(orient = 'records').replace('\\', ''))           
        
    except:
        output_json['error-message'] = 'Could not process request.'
    return json.dumps(output_json)
        

if __name__ == '__main__':
    app.debug = True
    app.run(debug = True, host = '0.0.0.0', port = 49517)