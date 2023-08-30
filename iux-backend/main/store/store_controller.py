from flask import Flask, request, jsonify, Blueprint
import sys
import json

#sys.path.insert(0, '/')

#from iux_custom_agent import agent_executor as agent
#from iux_agent import agent_executor as agent
from store.store_agent import func_agent as agent
#import gc

#from data_interface import cost_api, price_api, promotion_api, movement_api, hier_api
from store.store_dummy_data_interface import find_no_of_stores, group_stores_cluster, no_of_competing_stores
from store.store_data_location import root_dir
app = Flask(__name__)

# Create a blueprint
store_blueprint = Blueprint('store', __name__)

def get_file_path():
    file_name = 'competitor_store.pkl'
  #  return r'C:\Users\Dell\Desktop\New folder\Competitor_Store.xlsx' # enter excel file name 
    return root_dir + file_name

def find_no_of_stores_route(stores):
    file_path = get_file_path()
    api_key = 'AIzaSyBn6Qew7satVBa8Ai6R8cEBpawv59EIYGE' #'replace with google api key'
    cx = "16e561b6d18ab4463" #replace with google custom search engine id
    store_count = find_no_of_stores(file_path, stores, api_key, cx)
    # Convert the store_count to an integer
    store_count = int(store_count)
    # Prepare the result dictionary with string keys
    json_result = {
        'store_name': stores,
        'store_count': store_count
    }

    return json_result



def group_store_clusters_route(stores, no_of_groups, distance_stores, factors, within):
    file_path = get_file_path()
    cluster_summary_df, cluster_data_df = group_stores_cluster(file_path, stores, no_of_groups, distance_stores, factors, within)
    
    # Step 1: Store cluster_data_df as a .csv file
    filename = 'cluster_data.csv'
    csv_filename= root_dir +filename
    cluster_data_df.to_csv(csv_filename, index=False)
    
    # Step 2: Convert cluster_summary_df to JSON format
    cluster_summary_df['file_name'] = csv_filename  # Add the file_name column
     
    # Step 3: Convert cluster_summary_df to dictionary
    cluster_summary_json_data = cluster_summary_df.to_dict(orient='records')
    
    return  cluster_summary_json_data



def find_nearest_store_route(stores, competitors, within):
    file_path = get_file_path()
    count_miles = no_of_competing_stores(file_path, stores, competitors, within)
    return count_miles #{'count_miles': count_miles}




# Wrap your function into a REST API
@store_blueprint.route('/query_store_llm', methods=['POST'])
def add_endpoint():
    data = request.get_json()
    prompt = data.get('prompt')
    print(prompt)
    if not prompt :
        return jsonify ({'error': 'Please provide a prompt'}), 400
    ''' if not data or 'prompt' not in data:
        return jsonify({'error': 'Please provide a prompt'}), 400'''
    
    #print(data['prompt'])
    #result = agent.run(data['prompt'])
    result=agent.run(prompt)
    
    final_res = {'summary': result}
    print(final_res)

    '''with open('meta-data.json', 'r') as file:
        meta_data = json.load(file)

    final_res = {'summary': result, 'meta_data': meta_data}'''

    return json.dumps({'result' : final_res})


@store_blueprint.route('/find_no_of_stores', methods=['POST'])
def find_no_of_stores_handler():
    data = request.get_json()
    stores = data.get('stores')
    
    if stores:
     
        result = find_no_of_stores_route(stores)
       # Convert the store_count to an integer
        result['store_count'] = int(result['store_count'])
        
        # Convert the dictionary to a JSON string
        json_string = json.dumps(result)
        return json_string        
      
    else:
        return jsonify({'error': 'Missing stores parameter.'})
    
    
@store_blueprint.route('/group_stores', methods=['POST'])

def group_stores_handler():
    data = request.get_json()
    store_name = data.get('stores')
    no_of_groups = data.get('no_of_groups')
    distance_stores = data.get('distanceStores')
    factors = data.get('factors')
    within = data.get('distanceWithin') 
    
    if store_name and no_of_groups and distance_stores:
        cluster_summary_json_data = group_store_clusters_route(store_name, no_of_groups, distance_stores, factors, within)
        
        # Extract the CSV address
        csv_address = [entry['file_name'] for entry in cluster_summary_json_data][0]
        
        # Extract the cluster_summary_df JSON data
        
        # Create JSON response structure
        response = {
            'csv_address': csv_address,
            'type': 'table',
            'summary': cluster_summary_json_data  # This should directly contain your cluster summary DataFrame structure
        }
        
        return response
    else:
        return jsonify({'error': 'Missing required parameters.'})
    
'''def group_stores_handler():
    data = request.get_json()
    store_name = data.get('stores')
    no_of_groups = data.get('no_of_groups')
    distance_stores = data.get('distanceStores')
    factors = data.get('factors')
    
    if store_name and no_of_groups and distance_stores:
        result = group_store_clusters_route(store_name, no_of_groups, distance_stores, factors)
       
        json_string = json.dumps(result)
        return json_string 
        #return jsonify(result)
    else:
        return jsonify({'error': 'Missing required parameters.'})'''

    
@store_blueprint.route('/competing_stores_in_miles', methods=['POST'])
def find_nearest_store_handler():
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
        return jsonify({'error': 'Internal Server Error'}), e

if __name__ == '__main__':
    app.run(debug=True, port = 4007, host = '0.0.0.0')
    #app.run(debug=True, port = 8000, host = '20.228.231.91') #4007, 4008
