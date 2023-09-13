from flask import Flask, request, jsonify, Blueprint
import sys
import json
import logging
import requests
#sys.path.insert(0, '/')

#from iux_custom_agent import agent_executor as agent
#from iux_agent import agent_executor as agent
from store.store_agent import func_agent as agent
#import gc

#from data_interface import cost_api, price_api, promotion_api, movement_api, hier_api
from store.store_dummy_data_interface import find_no_of_stores, group_stores_cluster, no_of_competing_stores
from store.store_data_location import root_dir # change store.
app = Flask(__name__)

# Create a blueprint
store_blueprint = Blueprint('store', __name__)

def get_file_path():
    file_name = 'competitor_store.pkl'
  #  return r'C:\Users\Dell\Desktop\New folder\Competitor_Store.xlsx' # enter excel file name 
    return root_dir + file_name

def find_no_of_stores_route(stores, city, state):
    file_path = get_file_path()
    api_key = 'AIzaSyBn6Qew7satVBa8Ai6R8cEBpawv59EIYGE' #'replace with google api key'
    cx = "16e561b6d18ab4463" #replace with google custom search engine id
    store_count = find_no_of_stores(file_path, stores, city, state, api_key, cx)
    # Convert the store_count to an integer
    store_count = int(store_count)
    # Prepare the result dictionary with string keys
    json_result = {
        'store_name': stores,
        'store_count': store_count
    }

    return json_result



def group_store_clusters_route(stores, no_of_groups, distance_stores, factors, within, city, state, min_store, max_store):
    
        file_path = get_file_path()
        cluster_summary_df = group_stores_cluster(file_path, stores, no_of_groups, distance_stores, factors, within ,city, state, min_store, max_store)
        
        # Step 1: Store cluster_data_df as a .csv file
       # filename = 'cluster_data.csv'
       # csv_filename= root_dir +filename
       # cluster_data_df.to_csv(csv_filename, index=False)
        
        # Step 2: Convert cluster_summary_df to JSON format
       # cluster_summary_df['file_name'] = csv_filename  # Add the file_name column
         
        # Step 3: Convert cluster_summary_df to dictionary
        cluster_summary_json_data = cluster_summary_df.to_dict(orient='records')
        
        return  cluster_summary_json_data
    
    
def find_nearest_store_route(stores, competitors, within, city, state, nostore, geography):
    file_path = get_file_path()
    count_miles = no_of_competing_stores(file_path, stores, competitors, within, city, state, nostore, geography)
    return count_miles #{'count_miles': count_miles}




# Wrap your function into a REST API
@store_blueprint.route('/query_store_llm', methods=['POST'])
def add_endpoint():
 try:
       data = request.get_json()
       prompt = data.get('prompt')
       print(prompt)
       if not prompt :
           return jsonify ({'error': 'Please provide a prompt'}), 400
       ''' if not data or 'prompt' not in data:
           return jsonify({'error': 'Please provide a prompt'}), 400'''
   
       #print(data['prompt'])
       #result = agent.run(data['prompt'])
       try:
           result=agent.run(prompt)
           
           final_res = {'summary': result}
           print(final_res)
           return json.dumps({'result' : final_res})
       
       except requests.exceptions.RequestException as e:
            logging.error('API Request error: %s', e)
            error_message = "There was an issue in retrieving the data. Please try again later with valid store names"
            raise DataHTTPException(error_code="api_request_error", error_message=error_message, detail=str(e))
    
       except json.JSONDecodeError as e:
            logging.error('JSONDecodeError: %s', e)
            error_message = "Looks like we were unable to fetch data for given store names. Could you please try with some other stores."
            raise DataHTTPException(error_code="json_decode_error", error_message=error_message, detail=str(e))
            
       except CSVAddressNotFoundException as e:
            logging.error('CSV address not found: %s', e)
            response_data = e.to_dict()
            return json.dumps(response_data), 400  # Bad Request
        
       except OutputParserException as e:
           logging.error('OutputParserException: %s', e)
           error_message = "Could not parse LLM output: " + str(e)
           raise DataHTTPException(error_code="output_parser_error", error_message=error_message, detail=str(e))
        
       except Exception as e:
            logging.error('General error: %s', e)
            error_message = "Looks like we were unable to fetch data from given stores names. Could you please try rephrasing"
            raise DataHTTPException(error_code="Input error", error_message=error_message, detail=str(e))

 except DataHTTPException as e:
        response_data = e.to_dict()
        print(response_data)
        return json.dumps(response_data), 500  # Internal Server Error




@store_blueprint.route('/find_no_of_stores', methods=['POST'])
def find_no_of_stores_handler():
    try :
        data = request.get_json()
        stores = data.get('stores')
        city=data.get('city')
        state=data.get('state')  
        
        if stores:
            if not city :
                city='US'
            if not state:
                state = 'US'
            result = find_no_of_stores_route(stores, city, state)
           # Convert the store_count to an integer
            result['store_count'] = int(result['store_count'])
            # Convert the dictionary to a JSON string
            
            json_string = json.dumps(result)
            return json_string 
          
    except Exception as e:
            return jsonify({'error': 'Missing store parameters or Internal Server Error'}), e
    
    
@store_blueprint.route('/group_stores', methods=['POST'])

def group_stores_handler():
    try: 
        data = request.get_json()
        store_name = data.get('stores')
        no_of_groups = data.get('no_of_groups')
        distance_stores = data.get('distanceStores')
        factors = data.get('factors')
        within = data.get('distanceWithin')
        city = data.get('city')
        state = data.get('state')
        min_store = data.get('minStore')
        max_store = data.get('maxStore')
    
        if store_name is not None and no_of_groups is not None and distance_stores is not None:
            cluster_summary_json_data = group_store_clusters_route(store_name, no_of_groups, distance_stores, factors, within, city, state, min_store, max_store)
    
            if 'error' not in cluster_summary_json_data:
                # Extract the CSV address
                # csv_address = [entry['file_name'] for entry in cluster_summary_json_data][0]
    
                # Extract the cluster_summary_df JSON data
    
                # Create JSON response structure
                response = {
                    # 'csv_address': csv_address,
                    'type': 'table',
                    'summary': cluster_summary_json_data  # This should directly contain your cluster summary DataFrame structure
                }
    
                return response
            else:
                return {'error': 'Error in cluster_summary_json_data'}

    except KeyError as ke:
        return {'error': f'Missing key in JSON data: {str(ke)}'}
    
    except Exception as e:
        # Handle other exceptions gracefully
        error_message = str(e)
        return {'error': error_message}

 
@store_blueprint.route('/competing_stores_in_miles', methods=['POST'])
def find_nearest_store_handler():
   try:
        data = request.get_json()
        stores = data.get('stores')
        competitors = data.get('distanceStores')
        within = data.get('distanceWithin')
        city=data.get('city')
        state=data.get('state')
        nostore=data.get('nostore')
        geography=data.get('geography')

        '''if not stores or not competitors or not within:
            return jsonify({'error': 'Missing required parameters.'})'''
        if stores and competitors and within:
            result_list = find_nearest_store_route(stores, competitors, within, city, state, nostore, geography)
       
        count_miles_dict = {}
        for item in result_list:
            for store_name, data in item.items():
                count_miles_dict[store_name] = data
        
 
        json_string = json.dumps(count_miles_dict)
        return json_string

               
        
   except Exception as e:
        return jsonify({'error': 'Missing required parameters or Internal Server Error'}), e

class DataHTTPException(Exception):
    def __init__(self, error_code, error_message, detail=None):
        self.error_code = error_code
        self.error_message = error_message
        self.detail = detail

    def to_dict(self):
        return {
            "error_code": self.error_code,
            "error_message": self.error_message,
            "detail": self.detail
        }
    
class CSVAddressNotFoundException(DataHTTPException):
    def __init__(self, error_message):
        super().__init__(error_code="csv_address_not_found", error_message=error_message)

class OutputParserException(DataHTTPException):
    def __init__(self, error_message):
        super().__init__(error_code="output_parser_error", error_message=error_message)



if __name__ == '__main__':
    app.run(debug=True, port = 6034, host = '0.0.0.0')
    #app.run(debug=True, port = 8000, host = '20.228.231.91') #4007, 4008
