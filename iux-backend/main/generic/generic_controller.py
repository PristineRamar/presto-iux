
from flask import Flask, request, jsonify, Blueprint
import json
import gc
import pandas as pd
import string
import random
import nltk
from nltk import word_tokenize, pos_tag

#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')


from generic.generic_data_interface import cost_api, price_api, promotion_api, movement_api, hier_api, plotting_api
from generic.generic_data_config import port, log_filename
#from dummy_data_interface import cost_api, price_api, promotion_api, movement_api, hier_api
from datetime import datetime
from generic.generic_agent import summary_agent, plot_agent
from generic.generic_e_types import DataHTTPException

app = Flask(__name__)

# Create a blueprint
generic_blueprint = Blueprint('generic', __name__)

# Error messages for common errors
def error_handling(error):
    if error == 'timeframe':
        return ('parsing', 'We had trouble identifying the time period you mentioned. Can you try rephrasing?')
    if error == 'product':
        return ('parsing', 'We had trouble identifying the product(s) you mentioned. Can you try rephrasing?')
    if error == 'location':
        return ('parsing', 'We had trouble identifying the location(s) you mentioned. Can you try rephrasing?')
    if error == 'authorization':
        return ('authorization', 'I am sorry, but according to our system you are not authorized to see the requested product(s).')
    if error == 'missing_data':
        return ('missing_data', 'I am sorry, but the requested information is not available in our database.')
    if error == 'data_size':
        return ('data_size', 'I am sorry, but the requested data is too large to display on the UI.')
    if error == 'chart_type':
        return ('chart_type', 'I am sorry, but the requested chart type is not currently supported.')

def contains_any(target_string, keywords):
    return any(keyword in target_string for keyword in keywords)



def extract_product_name(current_prompt):
    # Tokenize and POS tag the current prompt
    tokens = word_tokenize(current_prompt)
    tags = pos_tag(tokens)

    # Initialize product_name as None
    product_name = None

    # Keywords that may precede the product name
    keywords = ["show", "display", "analyze", "product"]

    # Look for the first noun (NN) after a keyword
    for i, (word, tag) in enumerate(tags):
        if tag == 'NN' and any(keyword in current_prompt.lower() for keyword in keywords):
            product_name = word
            break

    return product_name

def get_prev_response(metadata):
    # Extract product and timeframe from metadata
    products = metadata['meta_data']['products'][0]
    timeframe = metadata['meta_data']['timeframe']
    locations = metadata['meta_data']['locations']
    prev_prompt = metadata['previous_prompt']
    current_prompt = metadata['prompt'].lower()

    timeframes = ["q1", "q2", "q3", "q4", "w1", "w2", "w3", "w4", "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8", "p9", "p10", "p11", "p12"]

    # Check if the product name is mentioned in the current prompt
    # Extract the product name from the current_prompt
    product_name = extract_product_name(current_prompt)
    if product_name :
        for product in products.split(','):
            if product.lower() in current_prompt:
                product_name = product.strip()
                break

    # Construct the result string based on conditions
    if locations != ['CHAIN']:
        result = f'{prev_prompt},{locations},{timeframe}' if product_name else f'{prev_prompt},{products},{locations},{timeframe}'
    else:
        result = f'{prev_prompt},{timeframe}' if product_name else f'{prev_prompt},{products},{timeframe}'

    # Remove the timeframe from the result if it's present in the current_prompt
    for tf in timeframes:
        result = result.replace(f',{timeframe}', '')

    return result



@generic_blueprint.errorhandler(DataHTTPException)
def handler(exc):
    content={"result": exc.error_message}
    content['result']['detail'] = exc.detail
    return json.dumps(content), 200

# Wrap your function into a REST API
@generic_blueprint.route('/health', methods=['POST'])
def health():
    return "Presto IUX backend is running..."

# Wrap your function into a REST API
@generic_blueprint.route('/query', methods=['POST'])
def add_endpoint():
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({'error': 'Please provide a prompt'}), 400
    
   # prompt = data['prompt']    
    user_id = data['user-id']
    # Step 1: Extract prompt and check for keywords
    current_prompt = data["prompt"]
    keywords = ["sales", "margin", "unit"]
    curr_intent = "sales" if any(keyword in current_prompt for keyword in keywords) else None

    # Step 2: Extract intent from data and compare with curr_intent
    intent_from_data = data.get("intent", "")


    if intent_from_data == "sales" or curr_intent == "sales":
        if intent_from_data:
            prompt1 = get_prev_response(data)
            prompt = f"lastprompt: {prompt1}, current: {current_prompt}"
        else:
          prompt = f"current: {current_prompt}"

      
    message_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    
    lc_prompt = prompt.lower()
    keywords_1 = ['plot', 'create', 'show', 'display', 'give', 'generate']
    keywords_2 = ['chart', 'graph', 'table', 'line', 'bar', 'trend']

    if contains_any(lc_prompt, keywords_1) and contains_any(lc_prompt, keywords_2):
        agent = plot_agent
    else:
        agent = summary_agent
   # 
    result = agent.run(prompt + f'The user id is {user_id}. The message id is {message_id}')

   # result = agent.run(data['prompt'] + f'The user id is {user_id}. The message id is {message_id}')
# =============================================================================
#     try:
#         result = json.loads(result)
#         if 'series' in result:
#             for s in result['series']:
#                 if s['name'] in ['sales', 'margin', 'reg-price', 'list-cost']:
#                     s['data'] = list((pd.Series(s['data']) / 11).round(2).values)
#                 if s['name'] in ['movement', 'visits']:
#                     s['data'] = [int(x) for x in list((pd.Series(s['data']) / 11).astype(int).values)]
#         result = json.dumps(result)
#     except:
#         result = result.split()
#         for j, word in enumerate(result):
#             if bool(re.match(r'\$[,\d]+.+', word)):
#                 decoded_word = round(float(word.replace('$', '').replace(',', '')) / 11, 2)
#                 result[j] = '${:,.2f}'.format(decoded_word)
#             if bool(re.match(r'[,\d]+.+', word)):
#                 decoded_word = round(float(word.replace('$', '').replace(',', '')) / 11, 2)
#                 result[j] = '{:,.2f}'.format(decoded_word)
#         result = ' '.join(result)
# =============================================================================            
                    
    with open(f'meta-data_{message_id}.json', 'r') as file:
        meta_data = json.load(file)

    final_res = {'summary': result, 'meta_data': meta_data, 'intent' : 'sales'}

    return jsonify({'result' : final_res})

@generic_blueprint.route('/cost', methods = ['POST'])
def cost():
     
    input_json = request.get_json()
    output_json = dict()
    
    with open('Log_{}.txt'.format(log_filename), 'a') as logfile:          
        logfile.write(pd.to_datetime(datetime.now()).strftime('%Y-%m-%d %I:%M:%S %p')
                      + '\n    API: Cost\n    Args: ' + json.dumps(input_json) + '\n\n')
     
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
                            user_id = input_json['user-id'],
                            change = input_json['change'] if 'change' in input_json else 'All')
        
        output_json['timeframe'] = response[3]
        output_json['locations'] = response[2]
        output_json['products'] = response[1]
        output_json['data'] = json.loads(response[0].to_json(orient = 'records').replace('\\', ''))        
        
    except ValueError as error:
        messages = error_handling(error.args[0])
        output_json['error-code'] = messages[0]
        output_json['error-message'] = messages[1]
    except:
        output_json['error-code'] = 'unclassified'
        output_json['error-message'] = 'I am sorry, but we could not process your request due to an unexpected internal error.'
        
    return json.dumps(output_json)
        

@generic_blueprint.route('/price', methods = ['POST'])
 
def price():
     
    input_json = request.get_json()
    output_json = dict()
    
    with open('Log_{}.txt'.format(log_filename), 'a') as logfile:        
        logfile.write(pd.to_datetime(datetime.now()).strftime('%Y-%m-%d %I:%M:%S %p')
                      + '\n    API: Price\n    Args: ' + json.dumps(input_json) + '\n\n')
     
    try:
        response = price_api(product_name = input_json['product-name'] if 'product-name' in input_json else None,
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
                             user_id = input_json['user-id'],
                             change = input_json['change'] if 'change' in input_json else 'All')
        
        output_json['timeframe'] = response[3]
        output_json['locations'] = response[2]
        output_json['products'] = response[1]
        output_json['data'] = json.loads(response[0].to_json(orient = 'records').replace('\\', ''))          
        
    except ValueError as error:
        messages = error_handling(error.args[0])
        output_json['error-code'] = messages[0]
        output_json['error-message'] = messages[1]
    except:
        output_json['error-code'] = 'unclassified'
        output_json['error-message'] = 'I am sorry, but we could not process your request due to an unexpected internal error.'
        
    return json.dumps(output_json)
        
        
@generic_blueprint.route('/promotion', methods = ['POST'])
 
def promo():
     
    input_json = request.get_json()
    output_json = dict()
    
    with open('Log_{}.txt'.format(log_filename), 'a') as logfile:        
        logfile.write(pd.to_datetime(datetime.now()).strftime('%Y-%m-%d %I:%M:%S %p')
                      + '\n    API: Promo\n    Args: ' + json.dumps(input_json) + '\n\n')
     
    try:
        response = promotion_api(product_name = input_json['product-name'] if 'product-name' in input_json else None,
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
                                 user_id = input_json['user-id'],
                                 promo_type = input_json['promo-type'] if 'promo-type' in input_json else None,
                                 page_no = input_json['page-no'] if 'page-no' in input_json else None,
                                 block_no = input_json['block-no'] if 'block-no' in input_json else None)
        
        output_json['timeframe'] = response[3]
        output_json['locations'] = response[2]
        output_json['products'] = response[1]
        output_json['data'] = json.loads(response[0].to_json(orient = 'records').replace('\\', ''))         
        
    except ValueError as error:
        messages = error_handling(error.args[0])
        output_json['error-code'] = messages[0]
        output_json['error-message'] = messages[1]
    except:
        output_json['error-code'] = 'unclassified'
        output_json['error-message'] = 'I am sorry, but we could not process your request due to an unexpected internal error.'
        
    return json.dumps(output_json)
        

@generic_blueprint.route('/movement', methods = ['POST'])
 
def move():
     
    input_json = request.get_json()
    output_json = dict()
    
    with open('Log_{}.txt'.format(log_filename), 'a') as logfile:        
        logfile.write(pd.to_datetime(datetime.now()).strftime('%Y-%m-%d %I:%M:%S %p')
                      + '\n    API: Movement\n    Args: ' + json.dumps(input_json) + '\n\n')
     
    try:
        response = movement_api(product_name = input_json['product-name'] if 'product-name' in input_json else None,
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
                                cal_type = input_json['cal-type'] if 'cal-type' in input_json else 'W',
                                promoted = input_json['promoted'] if 'promoted' in input_json else 'All',
                                user_id = input_json['user-id'],
                                group_name = input_json['grouping-name'] if 'grouping-name' in input_json else None)
        
        output_json['timeframe'] = response[3]
        output_json['locations'] = response[2]
        output_json['products'] = response[1]
        output_json['data'] = json.loads(response[0].to_json(orient = 'records').replace('\\', ''))           
        
    except ValueError as error:
        messages = error_handling(error.args[0])
        output_json['error-code'] = messages[0]
        output_json['error-message'] = messages[1]
    except:
        output_json['error-code'] = 'unclassified'
        output_json['error-message'] = 'I am sorry, but we could not process your request due to an unexpected internal error.'
        
    return json.dumps(output_json)


@generic_blueprint.route('/hierarchy', methods = ['POST'])
 
def hier():
     
    input_json = request.get_json()
    output_json = dict()
    
    with open('Log_{}.txt'.format(log_filename), 'a') as logfile:        
        logfile.write(pd.to_datetime(datetime.now()).strftime('%Y-%m-%d %I:%M:%S %p')
                      + '\n    API: Hierarchy\n    Args: ' + json.dumps(input_json) + '\n\n')
     
    try:
        response = hier_api(product_name = input_json['product-name'] if 'product-name' in input_json else None,
                            product_id = input_json['product-id'] if 'product-id' in input_json else None,
                            product_level = input_json['product-level'] if 'product-level' in input_json else None,
                            detail_level = 1,
                            other_levels = [5, 4, 3, 2, 1.5, 1])

        output_json['data'] = json.loads(response.to_json(orient = 'records').replace('\\', ''))           
        
    except ValueError as error:
        messages = error_handling(error.args[0])
        output_json['error-code'] = messages[0]
        output_json['error-message'] = messages[1]
    except:
        output_json['error-code'] = 'unclassified'
        output_json['error-message'] = 'I am sorry, but we could not process your request due to an unexpected internal error.'
        
    return json.dumps(output_json)



@generic_blueprint.route('/plotting', methods = ['POST'])
 
def plot():
     
    input_json = request.get_json()
    output_json = dict()
    
    with open('Log_{}.txt'.format(log_filename), 'a') as logfile:        
        logfile.write(pd.to_datetime(datetime.now()).strftime('%Y-%m-%d %I:%M:%S %p')
                      + '\n    API: Plotting\n    Args: ' + json.dumps({x:input_json[x] for x in input_json if x!='data'}) + '\n\n')
     
    try:
        response = plotting_api(data = input_json['data'],
                                plot_type = input_json['type'] if 'type' in input_json else 'table',
                                metric_cols = input_json['metric-cols'] if 'metric-cols' in input_json else 'sales',
                                product_col = input_json['product-col'] if 'product-col' in input_json else 'product-name',
                                location_col = input_json['location-col'] if 'location-col' in input_json else 'location-name')

        output_json = response       
        
    except ValueError as error:
        messages = error_handling(error.args[0])
        output_json['error-code'] = messages[0]
        output_json['error-message'] = messages[1]
    except:
        output_json['error-code'] = 'unclassified'
        output_json['error-message'] = 'I am sorry, but we could not process your request due to an unexpected internal error.'
        
    return json.dumps(output_json)
        

if __name__ == '__main__':
    port=6022
    app.run(debug=True, port = port, host = '0.0.0.0')
    #app.run(debug=True, port = 8000, host = '20.228.231.91')
