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
from config.app_config import config

def get_data_by_api(**kwargs):
    start=time.time()
    print(kwargs)

    api_name = 'getkvi'#kwargs.pop('api_name')
    print(api_name)

    if 'url' in kwargs:
        url = kwargs.pop('url')
    else:
        #url = 'http://127.0.0.1:7000/' 
        #url = 'http://127.0.0.1:3999/'
        url = config['kvi']['kvi_url']


    #if 'user-id' in kwargs:
    #    user_id = kwargs.pop('user-id')
    #else:
    #    user_id  = 'ejack'

    endpoint = url + api_name    
    #converted_dict = {key.replace('_', '-'): value for key, value in kwargs.items()}


    headers = {'Content-Type': 'application/json'}
    #args =  {'user-id': '111'} 
    #print(converted_dict)
    ##args =  {'user-id': user_id} 
    #converted_dict 
    #| {'user-id': user_id} 
    ##print(args)
    print(endpoint)
    print(headers)
    response = requests.post(endpoint, headers = headers, json = kwargs)

    if response.status_code == 200:
        data = response.json()
        for key in data:
            if isinstance(data[key], str) and data[key].startswith('[') and data[key].endswith(']'):
                data[key] = data[key][2:-2]
                    
        timestamp = time.strftime('%Y%m%d%H%M%S')
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        file_name = f'response_{timestamp}_{random_string}.json'

        with open(file_name, 'w') as file:
            json.dump(data, file)
            print(f'JSON data saved to {file_name}')
    else:
        print(f'Request failed with status code {response.status_code}')
        
    
    try:
        res = {}
        res = data['summary']
        #res['Primary KVI'] = data['Primary KVI']
        #res['Stats'] = data['stats']
        #res['Factor used']= data['Factor used']
        print(data['timeframe'])
        meta_keys = ['timeframe', 'locations', 'products']
        meta_data = {key: data[key] for key in meta_keys if key in data}
        print(meta_data)
        with open('meta-data.json', 'w') as file:
            json.dump(meta_data, file)
    except:
       res = data
       with open('error-message.json', 'w') as file:
           json.dump(res, file)
        
    end=time.time()-start
    print("time_taken: ", round(end, 2), "sec")      
    print(res)
        
    return res 
    
    '''
    df = pd.DataFrame(data['data'])
    cols = df.columns.tolist()

    res = {}
    res['data_file'] = file_name
    res['columns'] = cols

    meta_keys = ['timeframe', 'locations', 'products']
    meta_data = {key: data[key] for key in meta_keys if key in data}
    with open('meta-data.json', 'w') as file:
        json.dump(meta_data, file)

    return json.dumps(res) '''

#def post_process_data(data_file, action = 'mean', cols = 'sales', change = 'No'):

'''    
def post_process_data(data_file, action = 'mean', cols = 'sales'):

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

    return json_data '''

class APICallParameters(BaseModel):
    """Inputs for get_data_by_api"""
    '''api_name: str = Field(
        ...,
        description="APIs to call: 1. KVI API: it returns the list of KVI items for given product; ",
        enum=["getkvi"]
    )'''
    ANALYSIS_START_DATE: Optional[str] = Field(
        None,
        #alias="start-date",
        description="Can be used to specify that the user wants information from a certain date onwards, e.g., 'May 12, 2021'. Always return date format as 'yyyy-mm-dd'. If user had specified season like summer or winter try your best to give season start date for current year to identify current year use 2022-2023 for US region.  "
    )
    ANALYSIS_END_DATE: Optional[str] = Field(
        None,
        #alias="end-date",
        description="Same as ANALYSIS_START_DATE"
    )
    location_name: Optional[str] = Field(
        None,
        description="Used to specify the location the user wants data pertaining to. For example, 'Zone 620' or 'online stores' or 'BM11' would be valid ways of using this argument."
    )
    location_id: Optional[int] = Field(
        None,
        description="Used to specify the location id the user wants data pertaining to. For example, '2' or '483' would be valid ways of using this argument.",
    )
    product_name: Optional[str] = Field(
        None,
        description="Used to specify which product group the user wants data pertaining to. For example, 'Upper Respiratory', 'Milk Fresh', 'Tabletop'  or 'grocery' would be valid ways of using this argument."
    )
    product_id: Optional[int]= Field(
        None,
        description="Used to specify which product ID the user wants data pertaining to. For example, '26', '48',  or '58' would be valid ways of using this argument."
    )    
    no_of_primary_kvi: Optional[int] = Field(
        None,
        description= "To indicate number of Primery KVIs required.",
    )
    primary_kvi_pct: Optional[int] = Field(
        None,
        description="To indicate percent of Primery KVIs required out of total items.",
    )
    no_of_secondary_kvi: Optional[int] = Field(
        None,
        description="To indicate number of Secondary KVIs required.",
    )
    secondary_kvi_pct: Optional[int] = Field(
        None,
        description="To indicate percent of Secondary KVIs required out of total items.",
    )
    filter_by: Optional[List[str]]= Field(
        None,
        description="This is a filter to use, on the basis of which user wants to create list of KVI items.Leave fields blank if you are not sure do NOT make any assumptions. It can only take values like REVENUE, TRANSACTIONS, PURCHASE_FREQUENCY and AFFINITY. Give input filter in the from of list, For example: ['REVENUE', 'TRANSACTIONS'] .Interpretation  of some words for filter, visits : Transactions, sales : Revenue, household reach : Customer, frequency : Purchase Frequency.",
        enum=['REVENUE', 'CUSTOMER', 'TRANSACTIONS', 'PURCHASE_FREQUENCY']
    )
       

class PostProcessParameters(BaseModel):
    """Inputs for post_process_data"""
    data_file: str = Field(
        ...,
        description=" This is a Json output including List of KVI items and stats along with the filter used needs to be displayed as output"
    )
    '''cols: List[str] = Field(
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
