import os
import io
import requests
import json
import pandas as pd
import time
import random
import string
import logging
import datetime
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

from typing import Type
from typing import Optional, List
from pydantic import BaseModel, Field

from langchain.tools import BaseTool, StructuredTool, Tool, tool
import sys
sys.path.insert(0, '../store_data_api')

from store.store_data_location import root_dir #change store.
from config.app_config import config 
#root_dir = 'E:\\Users\\Chavi\\code_from_git1\\presto-iux\\iux-backend\\main\\store\\'

def get_data_by_api(**kwargs):
    
#try:
    start=time.time()
    print("kwargs",  kwargs)

    api_name = kwargs.pop('api_name')
    print("api_name", api_name)

    if 'url' in kwargs:
        url = kwargs.pop('url')
    else:
        url = config['agent']['api_url']
       #url = 'http://127.0.0.1:6034/'
        #url = 'http://65.61.166.184:5001/'
       # url=' http://172.26.16.193:8065/'
         #url='http://localhost/'

    if 'user-id' in kwargs:
        user_id = kwargs.pop('user-id')
    else:
        user_id  = 'ejack'

    endpoint = url + api_name
    #converted_dict = {key.replace('-', '_'): value for key, value in kwargs.items()}
    converted_dict = {key.replace('_', '-'): value for key, value in kwargs.items()}
    if api_name=='find_no_of_stores':
        for key, value_list in converted_dict.items():
            converted_dict[key] = value_list[0]
    
    if api_name=='group_stores':
        # Original dictionary

        # Extract values of 'stores' and 'no_of_groups' keys
        stores_value = converted_dict['stores'][0].strip('[]')
        distance_within = int(converted_dict['distanceWithin'][0].strip('[]')) if 'distanceWithin' in converted_dict else 5
        no_of_groups_value = int(converted_dict['no-of-groups'][0].strip('[]')) if 'no-of-groups' in converted_dict else 3
        city = converted_dict['city'][0].strip('[]') if 'city' in converted_dict else 'US'
        state = converted_dict['state'][0].strip('[]') if 'state' in converted_dict else 'US'
        min_store = int(converted_dict['minStore'][0].strip('[]')) if 'minStore' in converted_dict else 2
        max_store = int(converted_dict['maxStore'][0].strip('[]')) if 'maxStore' in converted_dict else 20000
        if 'factors' not in converted_dict:
            converted_dict['factors']=['LAT','LON']
            
        factors=converted_dict['factors']
        
        if 'factors' in converted_dict:
            factors_list = [word.strip() for word in factors]
            factors= fix_urbanicity(factors_list)
       
        # Update the dictionary with the modified values
        modified_dict = {
            'stores': stores_value,
            'no_of_groups': no_of_groups_value,
            'factors':factors,
            'distanceWithin':distance_within,
            'city':city,
            'state':state,
            'minStore': min_store,
            'maxStore':max_store 
        }
        
        # Copy the remaining key-value pairs from the original dictionary to the modified dictionary
        for key, value in converted_dict.items():
            if key not in modified_dict and key not in ['stores', 'no-of-groups','factors','distanceWithin', 'city','state', 'minStore','maxStore']:
                modified_dict[key] = value
        
        converted_dict=modified_dict
        
    if api_name=='competing_stores_in_miles':
            stores_value = converted_dict['stores'][0].strip('[]')
           # competitor_value = converted_dict['distanceStores'][0].strip('[]')
            competitor_value = converted_dict['distanceStores']
            distance_within = [int(dist) for dist in converted_dict['distanceWithin']] if 'distanceWithin' in converted_dict else [5]
            city = converted_dict['city'][0].strip('[]') if 'city' in converted_dict else 'US'
            state = converted_dict['state'][0].strip('[]') if 'state' in converted_dict else 'US'
            nostore = converted_dict['nostore'][0] if 'nostore' in converted_dict else False
            
           # geography_value = converted_dict['geography'][0].strip('[]') if 'geography' in converted_dict else None
           # if 'geography' in converted_dict and converted_dict['geography'] is not None:
            geography_value = converted_dict['geography'][0].strip('[]') if 'geography' in converted_dict else None
           # else:
               # geography_value = None
            modified_dict = {
                'stores': stores_value,
                'distanceStores': competitor_value,
                'distanceWithin':distance_within,
                'city':city,
                'state':state,
                'nostore':nostore,
                'geography':geography_value
                
            }
            converted_dict=modified_dict

        
    
    
   # if 'user-id' not in converted_dict:
       # converted_dict['user-id'] = 'ejack'

    headers = {'Content-Type': 'application/json'}
    
    
    print('endpoint' ,endpoint)
    print('headers',headers)
    print('dictionary',converted_dict)

    try:
        response = requests.post(url=endpoint, json=converted_dict)
        response.raise_for_status()
            
        if response.status_code == 200:
                data = response.json()
                 
                filename = f'response_{api_name}.json'
                file_name= root_dir + filename
                with open(file_name, 'w') as file:
                     json.dump(data, file)
                     print(f'JSON data saved to {file_name}')
                     
                     
                        
                if api_name == 'group_stores':
                    # if 'csv_address' in data:
                               #  csv_address=data['csv_address']
                                # df=pd.DataFrame(data['summary'])
                                # df=df.drop(['file_name'], axis=1)
                                 res = {}
                                 res['data_file'] = file_name
                                 res['data']=data['summary']
                                # res['columns'] = df.columns
                                # res['message']= f'You can download the complete data from this location {csv_address}'
                                 res['type']=data['type']
                                 
                    # else:
                        # raise ValueError("'We could not fetch data for the given combination")
                                 
                           
                               
                            
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
                              
  
    except requests.RequestException as e:
            logger.error(f'API Request failed: {e}')
            error_message = {"error_code": "api_error", "error_message": "API request error"}
            logging.error('Input JSON: %s', json.dumps(converted_dict, indent=2))
        
            if hasattr(response, 'status_code'):
                logger.error(f'Request failed with status code {response.status_code}')
                error_message = "Failed to call DATA API"
                error_code = response.status_code
                x_time = pd.to_datetime(datetime.datetime.now()).strftime('%Y-%m-%d %I:%M:%S %p')
                log_entry = {
                    'x_time': x_time,
                    'api_name': api_name,
                    'error': e
                }
                file_name_error = "error_log.txt"
                file_path_error = root_dir + file_name_error
        
                with open(file_path_error, "a") as log_file:
                    log_file.write(f"{log_entry['x_time']}:\n API Name : {log_entry['api_name']} \n GeneralError: {log_entry['error']}\n")
        
                if hasattr(response, 'text'):
                    logging.error('Response Content: %s', response.text)
                
                try:
                    response_json = response.json()
                    logging.error('Response Content (JSON): %s', json.dumps(response_json, indent=2))
                except json.JSONDecodeError as decode_error:
                    logging.error('JSONDecodeError: %s', decode_error)
                
                raise DataHTTPException(status_code=400, detail="Fail to fetch data.", error_code=error_code, error_message=error_message)


def plot_data(**kwargs):
   # data_file= f'E:/Users/Chavi/response_group_stores.json'
   try :
       
           # print("kwargs",  kwargs)
            start=time.time()
           # api_name = kwargs.pop('api_name')
            data_file=kwargs.pop('data_file')
           # type=kwargs.pop('type')
            
            with open(data_file, 'r') as file:
                data = json.load(file)
        
            df = pd.DataFrame(data['summary'])
           # df=df.drop(['file_name'], axis=1)
            df.columns = [col.replace('_', ' ').title() for col in df.columns]
            fixed_column_order = ['Cluster', 'Store Count', 'Store Names']
            # Slice the DataFrame to keep the first three columns fixed and reorder the remaining columns
            new_column_order = fixed_column_order + [col for col in df.columns if col not in fixed_column_order]
            df = df[new_column_order]
            
        
            res={}
            tableData1 = df.to_dict(orient='records')
           # csv_address =data['csv_address']
           # res = {'type': 'table',  'tableData1' : tableData1, 'message': f'You can download the complete data from this location {csv_address}'}
            res = {'type': 'table',  'tableData1' : tableData1}

            #json_data = json.dumps(res)
            end=time.time()-start
            print('time taken for plotting', round(end,2))
            return res
            
   except Exception as e:
           # Log other exceptions
           logging.error('Error: %s', e)
           file_name_error="error_log.txt"
           file_path_error=root_dir+file_name_error
           with open(file_path_error, "a") as log_file:
               log_file.write(f"GeneralError: {e}\n")

   

 


class APICallParameters(BaseModel):
    """Inputs for get_data_by_api"""
    api_name: str = Field(
        ...,
        description="APIs to call: 1. find_no_of_stores API: Use this API to count number of stores of given store name in a city or state. ; 2. competing_stores_in_miles API: Use this API to find number of another stores in a certian miles or miles of given main store in a city or state.  ; 3. group_stores API: Use this api to create 'groups or cluster'  of given stores. Arguments may have two different store names, factors and distance. Plot data in tabular format",
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
        description="distance within contains the number of miles for which store information is required. this should be collected as list. For example, 1 mile, 5 mile should be extracted as input [1,5]"
    )
    no_of_groups: Optional[List[str]] = Field(
        None,
        description="This contains the number of groups for which store clustering is required. For example: Create 10 groups of my stores."
    )
    factors: Optional[List[str]] = Field(
        None,
        description="This contains the factors on the basis of which user wants to create clusters. Map any of the factor like rural, suburban, urban under 'urbanicity', keep pthers factors as it is. While giving input factors will be from this list [urbanicity, state, city, geography, population density] For example : rural, suburban , urban comes under factor called urbanicity, we can have other factors like city, geography, population density"
    )
    city: Optional[List[str]] = Field(
        None,
        description="This contains the location like city for which user needs the information"
    )
    state: Optional[List[str]] = Field(
        None,
        description="This contains the location like 'state' for which user needs the information. Identify state correctly"
    )
    nostore: Optional[List[str]] = Field(
          None,
          description="Consider the following user query:'How many Giant Eagle stores don't or do not have an Aldi store within 5 miles?' Now, analyze the query and provide a response that takes into account the negation expressed by 'don't or do not'. Provide information on the Giant Eagle stores that do not have an Aldi store within 5 miles.Set nostore as True if negation exists o/w False"
      )
    geography: Optional[List[str]] = Field(
          None,
          description="This contains geographies for which user needs information.  For example : Northeast, Midwest, South, West"
      )
    minStore: Optional[List[str]] = Field(
          None,
          description="This contains minium stores to be used for grouping or clustering"
      )
    maxStore: Optional[List[str]] = Field(
          None,
          description="This contains maximum stores to be used for grouping or clustering"
      )

class PlotDataParameters(BaseModel):
    """Inputs for plot_data"""
    data_file: str = Field(
        ...,
        description="Data file to be loaded to get the Pandas Data Frame. It should have extension .json"
    )
    type: str = Field(
        ...,
        description= "The type of charts to plot",
        enum=[ "table"]
    )
    api_name: str = Field(
        ...,
        description="api_name for which the data plotting is taking place"
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

class DataHTTPException(Exception):
    def __init__(self, status_code, error_code, error_message, detail=None):
        self.status_code = status_code
        self.error_code = error_code
        self.error_message = error_message
        self.detail = detail

    def to_dict(self):
        error_dict = {
            "status_code": self.status_code,
            "error_code": self.error_code,
            "error_message": self.error_message,
        }
        if self.detail:
            error_dict["detail"] = self.detail
        return error_dict

class BadRequestException(DataHTTPException):
    def __init__(self, error_code, error_message, detail=None):
        super().__init__(400, error_code, error_message, detail)

class NotFoundException(DataHTTPException):
    def __init__(self, error_code, error_message, detail=None):
        super().__init__(404, error_code, error_message, detail)

class ServerErrorException(DataHTTPException):
    def __init__(self, error_code, error_message, detail=None):
        super().__init__(500, error_code, error_message, detail)
