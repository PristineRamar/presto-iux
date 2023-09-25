from flask import Flask, request, jsonify,Response,Blueprint
import sys
import json
sys.path.insert(0, './')
#from iux_custom_agent import agent_executor as agent
#from iux_agent import agent_executor as agent
from affinity.affinity_agent import func_agent as agent
from affinity.affinity_data_interface import affinity_api

app = Flask(__name__)

# Create a blueprint
affinity_blueprint = Blueprint('affinity', __name__)

# Wrap your function into a REST API
#@app.route('/getAffinity', methods=['POST'])
@affinity_blueprint.route('/getAffinity', methods=['POST'])
def add_endpoint():
    data = request.get_json()
    print(data)
    if not data or 'prompt' not in data:
        return jsonify({'error': 'Please provide a prompt'}), 400
    found_keyword = False
    print(data['prompt'])
    result = agent.run(data['prompt'])
    print(result)
    keywords = ["sorry", "apologize", "error","failed"]
    for keyword in range(len(keywords)):
        if keywords[keyword] in result:
           found_keyword = True
           break 
    # modified_table_data = [
    # {"Affinity Product": entry["data"], "Visits #": entry["Visits #"], "Visits %": entry["Visits %"]}
    # for entry in result["tableData1"]
    # ]
    
    # modified_table_data = [
    # {**entry, "Affinity Product": entry["data"]} for entry in result["tableData1"]
    # ]
    
    # result["tableData1"] = modified_table_data
    if found_keyword == True:
           error_data = {
                  "error_code": "Input Error",
                  "error_message": "Looks like we were unable to fetch data from the given product name or item id. Could you please try rephrasing?",
                  "detail": "Exception"
           }
           #response_data = json.dumps(error_data)
           final_res = error_data
           return jsonify({'result' : final_res})
    else:
        for entry in result["tableData1"]:
           entry["Affinity Product"] = entry["data"]
           del entry['data']
        
        is_base_item_present = any('Base Item' in entry for entry in result["tableData1"])
        if is_base_item_present:
            result["tableData1"] = [
                {"Base Item": entry["Base Item"], "Affinity Product": entry["Affinity Product"], **{key: value for key, value in entry.items() if key not in ("Base Item", "Affinity Product")}}
                for entry in result["tableData1"]
                ]
        else:
            result["tableData1"] = [
                {"Affinity Product": entry["Affinity Product"], **{key: value for key, value in entry.items() if key not in ("Base Item", "Affinity Product")}}
                for entry in result["tableData1"]
                ]
        # with open('meta-data.json', 'r') as file:
        #     meta_data = json.load(file)
    
        #final_res = {'summary': result, 'meta_data': meta_data}
        final_res = {'summary': result}   
        response_data = json.dumps({'result' : final_res})
        #return jsonify({'result' : final_res})
        return Response(response_data, content_type="application/json")

@affinity_blueprint.route('/affinity', methods = ['POST'])

def affinity():
    print('Reached Here')
    input_json = request.get_json()
    #return jsonify({'Success':input_json})
    output_json = dict()
    print('Reached Here')
    input_json = json.dumps(input_json)
    input_json = json.loads(input_json)
    print(input_json)
    with open('log.txt', 'a') as logfile:        
        #logfile.write(pd.to_datetime(datetime.now()).strftime('%Y-%m-%d %I:%M:%S %p') + '\n')
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
        print('Reached Here')
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
    app.run( port = 49517, host = '0.0.0.0')
    #app.run(debug=True, port = 9000, host = '20.228.231.91')
