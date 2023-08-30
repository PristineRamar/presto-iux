import os
import io
import requests
import json
import pandas as pd
import time
import random
import string

from typing import Type
from typing import Optional, List
from pydantic import BaseModel, Field

from langchain.tools import BaseTool, StructuredTool, Tool, tool
import sys
sys.path.insert(0, '../store_data_api')

from store.store_data_location import root_dir
from config.app_config import config


def get_data_by_api(**kwargs):
    start=time.time()
    print("kwargs",  kwargs)

    api_name = kwargs.pop('api_name')
    print("api_name", api_name)

    if 'url' in kwargs:
        url = kwargs.pop('url')
    else:
        url = config['agent']['api_url']
       #url = 'http://127.0.0.1:4008/'
       #url = 'http://65.61.166.184:5001/'
       #url=' http://172.26.16.193:8065/'
       #url='http://localhost/'

    if 'user-id' in kwargs:
        user_id = kwargs.pop('user-id')
    else:
        user_id = config['agent']['user_id']

    endpoint = url + api_name
    #converted_dict = {key.replace('-', '_'): value for key, value in kwargs.items()}
    converted_dict = {key.replace('_', '-'): value for key, value in kwargs.items()}
    if api_name=='find_no_of_stores':
        for key, value_list in converted_dict.items():
            converted_dict[key] = value_list[0]
    
    if api_name=='group_stores':
        # Original dictionary

        # Extract values of 'stores' and 'no_of_groups' keys
        stores_value = converted_dict['stores'][0]
        no_of_groups_value = converted_dict['no-of-groups'][0]
        factors=converted_dict['factors']
    
        if 'distanceWithin' in converted_dict:
            distance_within=converted_dict['distanceWithin'][0]
            distance_within = distance_within.strip('[]')
        else:
           distance_within='5'
            
        factors_list = [word.strip() for word in factors]
        factors= fix_urbanicity(factors_list)
        # Remove brackets from the extracted values
        stores_value = stores_value.strip('[]')
        no_of_groups_value = no_of_groups_value.strip('[]')
        
        # Convert 'no_of_groups' value to integer (optional)
        no_of_groups_value = int(no_of_groups_value)
        # Update the dictionary with the modified values
        modified_dict = {
            'stores': stores_value,
            'no_of_groups': no_of_groups_value,
            'factors':factors,
            'distanceWithin':distance_within
        }
        
        # Copy the remaining key-value pairs from the original dictionary to the modified dictionary
        for key, value in converted_dict.items():
            if key not in modified_dict and key not in ['stores', 'no-of-groups','factors','distanceWithin']:
                modified_dict[key] = value
        
        converted_dict=modified_dict
        
    if api_name=='competing_stores_in_miles':
            stores_value = converted_dict['stores'][0]
            competitor_value = converted_dict['distanceStores'][0]
            distance_within=[int(dist) for dist in converted_dict['distanceWithin']]
            
            stores_value = stores_value.strip('[]')
            #competitor_value=competitor_value
            competitor_value = competitor_value.strip('[]')
            # Update the dictionary with the modified values
            modified_dict = {
                'stores': stores_value,
                'distanceStores': competitor_value,
                'distanceWithin':distance_within
            }
            converted_dict=modified_dict

        
    
    
   # if 'user-id' not in converted_dict:
       # converted_dict['user-id'] = 'ejack'

    headers = {'Content-Type': 'application/json'}
    #args =  {'user-id': '111'} 
    #print(converted_dict)
   # args =  {'user-id': user_id} 
    #converted_dict 
    #| {'user-id': user_id} 
   
   # print('args' , args)
    
    print('endpoint' ,endpoint)
    print('headers',headers)
    print('dictionary',converted_dict)
    #response = requests.post(endpoint, headers = headers, json = converted_dict)
   
    response = requests.post(endpoint, json = converted_dict)
    #===============================================================
    #url=endpoint
    ''' try:
        response = requests.post(url=endpoint, json=converted_dict)
        response.raise_for_status()  # Raises an HTTPError for non-2xx responses
    
        end = time.time()
       # print_system_utilization()
        print('Time Taken: {}'.format(round(end - start, 2)))
    
        response_data = response.json()
        print(response_data)
    except requests.exceptions.RequestException as e:
        # This handles any connection errors or HTTP-related issues
        print('Error:', e)
        print('Input JSON:', json.dumps(converted_dict, indent=2))  # Display input JSON in console
        with open("error_log.txt", "a") as log_file:
            log_file.write(f"Error: {e}\nInput JSON: {json.dumps(converted_dict)}\n")
    except json.JSONDecodeError as e:
        # This handles the JSONDecodeError when the response does not contain valid JSON
        print('JSONDecodeError:', e)
        print('Response Content:', response.text)  # Display response content in console
        with open("error_log.txt", "a") as log_file:
            log_file.write(f"JSONDecodeError: {e}\nResponse Content: {response.text}\n")'''
    #=============================================================================================================
    if response.status_code == 200:
       data = response.json()
      # timestamp = time.strftime('%Y%m%d%H%M%S')
      # random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    
       filename = f'response_{api_name}.json'
       file_name= root_dir + filename
       with open(file_name, 'w') as file:
           json.dump(data, file)
           print(f'JSON data saved to {file_name}')
   
    else:
        print(f"Request failed with status code: {response.status_code}")
        
    print("result", data)
    
    if api_name == 'group_stores':
        csv_address=data['csv_address']
        df=pd.DataFrame(data['summary'])
        df=df.drop(['file_name'], axis=1)
        res = {}
        res['data_file'] = file_name
        res['data']=data['summary']
       # res['columns'] = df.columns
        res['message']= f'You can download the complete data from this location {csv_address}'
        res['type']=data['type']
        

        return res
        '''csv_address = data['csv_address']
            summary = data['summary']
            response_type = 'table'  # You can adjust this based on your needs
                
                # Create the response dictionary
            res = {
                    'csv_address': csv_address,
                    'summary': {
                        'type': response_type,
                        'data': summary
                    },
                    'message': f'You can download the complete data from this location {csv_address}'
            }'''
     
   
    
    
    else:
      
        df = pd.DataFrame([data], index=[0])
        
            #print(df)
        cols = df.columns.tolist()
        res = {}
        res['data_file'] = data
        res['columns'] = cols

    ''' meta_keys =cols # ['timeframe', 'locations', 'products']
    meta_data = {key: data[key] for key in meta_keys if key in data}
    with open('meta-data.json', 'w') as file:
        json.dump(meta_data, file)'''
        
    end=time.time()-start
    print("time_taken: ", round(end, 2), "sec")
    
    return res
    
   
   # return response
    '''if response.status_code == 200:
        data = response.json()
        timestamp = time.strftime('%Y%m%d%H%M%S')
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        file_name = f'response_{timestamp}_{random_string}.json'

        with open(file_name, 'w') as file:
            json.dump(data, file)
            #print(f'JSON data saved to {file_name}')
    else:
        print(f'Request failed with status code {response.status_code}')
    print("result is", data)
    df = pd.DataFrame(data['data'])
    cols = df.columns.tolist()

    res = {}
    res['data_file'] = file_name
    res['columns'] = cols

    meta_keys = ['timeframe', 'locations', 'products']
    meta_data = {key: data[key] for key in meta_keys if key in data}
    with open('meta-data.json', 'w') as file:
        json.dump(meta_data, file)

    return json.dumps(res)'''

#def post_process_data(data_file, action = 'mean', cols = 'sales', change = 'No'):
    

        
'''def post_process_data(data_file, action = 'mean', cols = 'sales'):

    with open(data_file, 'r') as file:
        data = json.load(file)
    df = pd.DataFrame(data['data'])

    print(cols)
    if isinstance(cols, str):
        cols = [word.strip() for word in cols.split(',')]
    print(cols)

    #if action == 'list' and change == 'Yes':
        #df_grouped = df.groupby('item-name')[cols].nunique()
        #items = df_grouped[df_grouped == 1].index.tolist()
        #if len(items) <= 10:
            #json_data = json.dumps(items)
        #else:
            #json_data = json.dumps(items[:10])
    #elif action == 'list':
    if action == 'list':
        items = df['item-name'].unique().tolist()
        if len(items) <= 10:
            json_data = json.dumps(items)
        else:
            json_data = json.dumps(items[:10])
    else:
        res = df[cols].apply(action)
        json_data = json.dumps(res.to_json())

    return json_data'''

def plot_data(data_file, type = 'table'):

   # data_file= f'E:/Users/Chavi/response_group_stores.json'

    with open(data_file, 'r') as file:
        data = json.load(file)

    df = pd.DataFrame(data['summary'])
    df=df.drop(['file_name'], axis=1)
    df.columns = [col.replace('_', ' ').title() for col in df.columns]
    fixed_column_order = ['Cluster', 'Store Count', 'Store Names']
    # Slice the DataFrame to keep the first three columns fixed and reorder the remaining columns
    new_column_order = fixed_column_order + [col for col in df.columns if col not in fixed_column_order]
    df = df[new_column_order]
    


    tableData1 = df.to_dict(orient='records')
    csv_address =data['csv_address']
    res = {'type': 'table',  'tableData1' : tableData1, 'message': f'You can download the complete data from this location {csv_address}'}
    #json_data = json.dumps(res)
    return res


class APICallParameters(BaseModel):
    """Inputs for get_data_by_api"""
    api_name: str = Field(
        ...,
        description="APIs to call: 1. find_no_of_stores API: Use this when only one store name is given. This API returns number of stores for the given store name; 2. competing_stores_in_miles API: when a user asks to find number or how many given stores are within few miles of competing store, we use this API. It returns the count of competitor stores of the given stores within the miles/radius of a given store. ; 3. group_stores API: it returns the clusters or groups of stores given the store name, competitior/distance/nearby stores name, no of groups and factors, By default we have set a distance of competing store as 5 miles.on the basis of this clustering should take place. plot the data in tabular format",
        enum=["find_no_of_stores, competing_stores_in_miles, group_stores"]
    )
    
    stores: Optional[List[str]] = Field(
        None,
        description="A store name for which users want to get information for.Note that store name is a string, not a list. For example : 'cvs', 'walmart' "
    )
    distanceStores: Optional[List[str]] = Field(
        None,
        description="Competitior store names  for which users want to get information for in comparison with their store .For example : 'walgreens', 'walmart' "
    )
    distanceWithin: Optional[List[str]] = Field(
        None,
        description="distance within contains the numbe of milesfor which store information is required. this should be collected as list. For example, 1 mile, 5 mile should be extracted as input [1,5]"
    )
    no_of_groups: Optional[List[str]] = Field(
        None,
        description="This contains the number of groups for which store clustering is required. For example: Create 10 groups of my stores."
    )
    factors: Optional[List[str]] = Field(
        None,
        description="This contains the factors on the basis of which user wants to create clusters. Map any of the factor like rural, suburban, urban under 'urbanicity', keep pthers factors as it is. While giving input factors will be from this list [urbanicity, state, city, geography, population density] For example : rural, suburban , urban comes under factor called urbanicity, we can have other factors like city, geography, population density"
    )
   
    '''product_name: Optional[List[str]] = Field(
        None,
        description="Used to specify which product group the user wants data pertaining to. For example, 'Upper Respiratory', 'OTC internal',  or 'grocery' would be valid ways of using this argument."
    )
    item_list: Optional[List[str]] = Field(
        None,
        description="A list of items the user wants data pertaining to."
    )
    location_name: Optional[List[str]] = Field(
        None,
        description="Used to specify the location the user wants data pertaining to. For example, 'Zone 620' or 'online stores' would be valid ways of using this argument."
    )
    week: Optional[List[str]] = Field(
        None,
        description="Can be used to specify specific weeks in the retail calendar, e.g., ['7'] or ['46', '47', '48']. Alternatively, the user can specify certain weeks using key phrases such as 'current', 'last 4', or 'next 6'."
    )
    period: Optional[List[str]] = Field(
        None,
        description="Can be used to specify specific periods in the retail calendar, e.g., ['4'] or  ['5', '6']. Alternatively, the user can specify certain periods using key phrases such as 'current', 'last 1', or 'next 2'."
    )
    quarter: Optional[List[str]] = Field(
        None,
        description="Can be used to specify specific quarters in the retail calendar, e.g., ['1'] or  ['2', '3']. Alternatively, the user can specify certain quarters using key phrases such as 'current', 'last 1', or 'next 2'."
    )
    cal_year: Optional[List[str]] = Field(
        None,
        #alias="cal-year",
        description="Can be used to specify specific years in the retail calendar, e.g., ['2021'] or  ['2022', '2023']. Alternatively, the user can specify certain years using key phrases such as 'current', 'last 1', or 'next 2'."
    )
    start_date: Optional[str] = Field(
        None,
        #alias="start-date",
        description="Can be used to specify that the user wants information from a certain date onwards, e.g., 'May 12, 2021'."
    )
    end_date: Optional[str] = Field(
        None,
        #alias="end-date",
        description="Same as start-date"
    )
    change: Optional[str] = Field(
        None,
        description= "A flag to indicate if the query is about change. This flag only applis to cost and price APIs.",
        enum=["All", "Yes", "No"]
    )
    promoted: Optional[str] = Field(
        None,
        description="A flag that only applies to Movement API.",
        enum=["Yes", "No", "All"]
    )
    promo_type: Optional[str] = Field(
        None,
        description="A flag that only applies to Promotion API.",
        enum=["Stardard", "BOGO"]
    )
    page_no: Optional[int] = Field(
        None,
        description="A flag that only applies to Promotion API: the page no of the promotion",
    )
    block_no: Optional[int] = Field(
        None,
        description="A flag that only applies to Promotion API: the block no of the promotion",
    )'''

'''class PostProcessParameters(BaseModel):
    """Inputs for post_process_data"""
    response: str = Field(
        ...,
        description="This is json output obtained after running StoreClusteringTool"
    )
    cols: List[str] = Field(
        ...,
        description="Column or list of columns selected for post processing."
    )
    action: str = Field(
        ...,
        description= "A function to be applied to the Data Frame",
        #enum=["mean", "sum", "detect-change", "list"]
        #enum=["mean", "sum", "detect-change"]
        enum=["mean", "sum", "list"]
    )'''

class PlotDataParameters(BaseModel):
    """Inputs for plot_data"""
    data_file: str = Field(
        ...,
        description="Data file to be loaded to get the Pandas Data Frame."
    )
    type: str = Field(
        ...,
        description= "The type of charts to plot",
        enum=[ "table"]
    )
    
    

def fix_urbanicity(factors):
    urbanicity_factors = ['rural', 'urban', 'suburban']
    updated_list = []

    for word in factors:
        word = word.strip(', ')
        if word in urbanicity_factors:
            updated_list.append('urbanicity')
        else:
            updated_list.append(word)

    # Drop duplicates using set and preserve the order using list comprehension
    updated_list = list(dict.fromkeys(updated_list))

    #print("Updated list:", updated_list)
    return updated_list