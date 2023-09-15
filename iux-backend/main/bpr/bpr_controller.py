from flask import Flask, request, jsonify, Blueprint
import sys
import json
sys.path.insert(0, './')
from bpr.bpr_agent import func_agent as agent
from bpr.bpr_api import suggest_promo_to_meet_goals as suggest_promo_to_meet_goals

app = Flask(__name__)
bpr_blueprint = Blueprint('bpr', __name__)

# Wrap your function into a REST API
@bpr_blueprint.route('/get-bpr-data', methods=['POST'])  
def bpr_results():
    input_json = request.get_json()
   # input_json = json.loads(input_json)
    output_json = dict()
    result = suggest_promo_to_meet_goals(week = input_json['week'] if 'week' in input_json else None,
    period = input_json['period'] if 'period' in input_json else None,
    quarter = input_json['quarter'] if 'quarter' in input_json else None,
    location_name = input_json['location_name'] if 'location_name' in input_json else 'N',
    location_id = input_json['location_id'] if 'location_id' in input_json else None,
    product_name=input_json['product_name'][0] if 'product_name' in input_json else None,
    product_id = input_json['product_id'] if 'product_id' in input_json else None) # using renamed function0
    #print(result)
    output_json['data'] = result
    
    return json.dumps(output_json) 


@bpr_blueprint.route('/query-bpr', methods=['POST']) 
def add_endpoint():
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({'error': 'Please provide a prompt'}), 400
    
    print(data['prompt'])
    result = agent.run(data['prompt'])

    with open('meta-data.json', 'r') as file:
        meta_data = json.load(file)

    keywords = ["sorry", "apologize", "error"]
    for keyword in range(len(keywords)):
       if keywords[keyword] in result:
           with open('error-message.json', 'r') as file:
               final_res = json.load(file)
                      
           print(final_res)
           break      
    
    else:
        final_res = {'summary': result, 'meta_data': meta_data}
        print(final_res)
            

    return jsonify({'result' : final_res})

if __name__ == '__main__':
    app.run(debug=True, port = 9098, host = '0.0.0.0')
    #app.run(debug=True, port = 8000, host = '20.228.231.91')
