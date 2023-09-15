# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 14:34:19 2023

@author: Ashutosh
"""

from flask import Flask, request, jsonify
import json
import gc
import pandas as pd

from affinity.affinity_data_interface import affinity_api
#from dummy_data_interface import cost_api, price_api, promotion_api, movement_api, hier_api
from datetime import datetime
 
app = Flask(__name__)  
  

@app.route('/affinity', methods = ['POST'])

def affinity():
    print('Reached Here')
    input_json = request.get_json()
    #return jsonify({'Success':input_json})
    output_json = dict()
    print('Reached Here')
    input_json = json.dumps(input_json)
    input_json = json.loads(input_json)
    with open('log.txt', 'a') as logfile:        
        logfile.write(pd.to_datetime(datetime.now()).strftime('%Y-%m-%d %I:%M:%S %p') + '\n')
        logfile.write('4')
        logfile.write('    API: Movement\n')
        #logfile.write('    Args: ' + input_json['product-name'] + '\n\n')
        #logfile.write(' '.join(affinity_api(input_json['product-name'][0] if 'product-name' in input_json else None,'eJack')))
       
   
    
    try:
        # response = affinity_api('ICE CREAM SINGLE DIP',
        #                         #product_name = input_json['product-name'][0] if 'product-name' in input_json else None,
        #                         # product_id = input_json['product-id'] if 'product-id' in input_json else None,
        #                         # product_level = input_json['product-level'] if 'product-level' in input_json else None,
        #                         # item_list = input_json['item-list'] if 'item-list' in input_json else None,
        #                         # active = input_json['active'] if 'active' in input_json else 'Y',
        #                         # location_name = input_json['location-name'] if 'location-name' in input_json else None,
        #                         # location_id = input_json['location-id'] if 'location-id' in input_json else None,
        #                         # location_level = input_json['location-level'] if 'location-level' in input_json else None,
        #                         # cal_year = input_json['cal-year'] if 'cal-year' in input_json else None,
        #                         # quarter = input_json['quarter'] if 'quarter' in input_json else None,
        #                         # period = input_json['period'] if 'period' in input_json else None,
        #                         # week = input_json['week'] if 'week' in input_json else None,
        #                         # day = input_json['day'] if 'day' in input_json else None,
        #                         # start_date = input_json['start-date'] if 'start-date' in input_json else None,
        #                         # end_date = input_json['end-date'] if 'end-date' in input_json else None,
        #                         # calendar_id = input_json['calendar-id'] if 'calendar-id' in input_json else None,
        #                         # cal_type = input_json['cal-type'] if 'cal-type' in input_json else None,
        #                         # promoted = input_json['promoted'] if 'promoted' in input_json else 'All',
        #                         'eJack'
        #                         #user_id = input_json['user-id'][0]
        #                         )
        
        if 'product-name' in input_json:
            value = input_json['product-name'][0]
        elif 'item-list' in input_json:
            value = input_json['item-list'][0]
        print(value)    
        response = affinity_api(value,'eJack')
     
        # output_json['timeframe'] = response[3]
        # output_json['locations'] = response[2]
        # output_json['products'] = response[1]
        #output_json['data'] = json.loads(response[0].to_json(orient = 'records').replace('\\', ''))           
        output_json = response.to_json()
    except:
        print(output_json)
        output_json['error-message'] = 'Could not process request.'
    return json.dumps(output_json)        

if __name__ == '__main__':
    app.debug = True
    app.run(debug = True, host = '0.0.0.0', port = 49517)