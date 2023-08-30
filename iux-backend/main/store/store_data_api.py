# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 14:34:19 2023

@author: Dan
"""

from flask import Flask, request, jsonify
import json
#import gc

#from data_interface import cost_api, price_api, promotion_api, movement_api, hier_api
from store_dummy_data_interface import find_no_of_stores, group_stores_cluster, no_of_competing_stores
from store_data_location import root_dir
 
app = Flask(__name__)  


#======================================================================================================


'''def find_nearest_store_handler():
    try:
        data = request.get_json()
        stores = data.get('stores')
        competitors = data.get('distanceStores')
        within = data.get('distanceWithin')


        if not stores or not competitors or not within:
            return jsonify({'error': 'Missing required parameters.'}), 400

        result = find_nearest_store_route(stores, competitors, within)
        result = {str(key): int(value) for key, value in result.items()}
        # Convert the dictionary to a JSON string
        json_string = json.dumps(result)
        return json_string

    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500'''
    
 #==================================================================================   
'''def find_nearest_store_handler():
    data = request.get_json()
    stores = data.get('stores')
    competitors = data.get('distanceStores')
    within = data.get('distanceWithin')

    if stores and competitors and within:
        result = find_nearest_store_route(stores, competitors, within)
        return jsonify(result)
    else:
        return jsonify({'error': 'Missing required parameters.'})'''
#==================================================================================================  

'''@app.route('/cost', methods = ['POST'])
 
def cost():
     
    input_json = request.get_json()
    output_json = dict()
    print(input_json)
     
    try:
        response = cost_api(product_name = input_json['product-name'] if 'product-name' in input_json else None,
                            product_id = input_json['product-id'] if 'product-id' in input_json else None,
                            product_level = input_json['product-level'] if 'product-level' in input_json else None,
                            item_list = input_json['item-list'] if 'item-list' in input_json else None,
                            active = input_json['active'] if 'active' in input_json else 'Y',
                            location_name = input_json['location-name'] if 'location-name' in input_json else None,
                            location_id = input_json['location-id'] if 'location-id' in input_json else None,
                            location_level = input_json['location-level'] if 'location-level' in input_json else None,
                            cal_year = input_json['cal-year'] if 'cal-year' in input_json else None,
                            quarter = input_json['quarter'] if 'quarter' in input_json else None,
                            period = input_json['period'] if 'period' in input_json else None,
                            week = input_json['week'] if 'week' in input_json else None,
                            day = input_json['day'] if 'day' in input_json else None,
                            start_date = input_json['start-date'] if 'start-date' in input_json else None,
                            end_date = input_json['end-date'] if 'end-date' in input_json else None,
                            calendar_id = input_json['calendar-id'] if 'calendar-id' in input_json else None,
                            cal_type = input_json['cal-type'] if 'cal-type' in input_json else None,
                            user_id = input_json['user-id'])
        
        output_json['timeframe'] = response[3]
        output_json['locations'] = response[2]
        output_json['products'] = response[1]
        output_json['data'] = json.loads(response[0].to_json(orient = 'records').replace('\\', ''))        
        
    except:
        output_json['error-message'] = 'Could not process request.'
    return json.dumps(output_json)'''
        


        
'''if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0')'''
    
if __name__ == '__main__':
    port=4008 #6122 # specify desired port 
    app.run(debug=True, port=port)


