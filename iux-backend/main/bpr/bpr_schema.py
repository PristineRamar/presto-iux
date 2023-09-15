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
from config.app_config import config
from langchain.tools import BaseTool, StructuredTool, Tool, tool
  

def get_data_by_api(**kwargs):
    start=time.time()
    print(kwargs)

    api_name = 'get-bpr-data'#kwargs.pop('api_name')
    print(api_name)

    if 'url' in kwargs:
        url = kwargs.pop('url')
    else:
        url = config['agent']['api_url']


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
    print (response)

    if response.status_code == 200:
        data = response.json()
        '''for key in data:
            if isinstance(data[key], str) and data[key].startswith('[') and data[key].endswith(']'):
                data[key] = data[key][2:-2]'''
                    
        timestamp = time.strftime('%Y%m%d%H%M%S')
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        file_name = f'response_{timestamp}_{random_string}.json'

        with open(file_name, 'w') as file:
            json.dump(data, file)
            print(f'JSON data saved to {file_name}')
    else:
        print(f'Request failed with status code {response.status_code}')
        
    
    try:
        df = data['data']
        df = json.loads(df['Data'])
        df = pd.DataFrame(df)
        cols = df.columns.tolist()
        res = {}
        res['data_file'] = file_name
        print(file_name)
        res['df'] = df
        res['columns'] = cols

        print(data['data']['timeframe'])
        meta_keys = ['timeframe', 'locations', 'products']
        meta_data = {key: data['data'][key] for key in meta_keys if key in  data['data']}
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
    
    
def plot_data(data_file, type = 'table'):
    print('plot_data start')
    with open(data_file, 'r') as file:
        data = json.load(file)

    df = data['data']['Data']
    df = json.loads(df)

    print(df)
    df = pd.DataFrame(df)
    #df=df.drop(['file_name'], axis=1)
    df.columns = [col.replace('_', ' ').title() for col in df.columns]
    print(df.columns )
    fixed_column_order = ['Category Name','Product Level Id','Ret Lir Name', 'Item Name','Retailer Item Code','Start Date', 'End Date']
    # Slice the DataFrame to keep the first three columns fixed and reorder the remaining columns
    new_column_order = fixed_column_order + [col for col in df.columns if col not in fixed_column_order]
    df = df[new_column_order]    
    tableData1 = df.to_dict(orient='records')
    #print(tableData1)
    res = {'type': 'table',  'tableData1' : tableData1}
    print(res)
    #json_data = json.dumps(res)
    return res


class APICallParameters(BaseModel):
    """Inputs for get_data_by_api"""
    '''api_name: str = Field(
        ...,
        description="APIs to call: 1. KVI API: it returns the list of KVI items for given product; ",
        enum=["getkvi"]
    )'''
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
    location_name: Optional[str] = Field(
        None,
        description="Used to specify the location the user wants data pertaining to. For example, 'Zone 620' or 'online stores' would be valid ways of using this argument."
    )
    location_id: Optional[int] = Field(
        None,
        description="Used to specify the location id the user wants data pertaining to. For example, '2' or '483' would be valid ways of using this argument.",
    )
    product_name: Optional[str] = Field(
        None,
        description="Used to specify which product group the user wants data pertaining to. For example, 'Upper Respiratory', 'OTC internal',  or 'grocery' would be valid ways of using this argument."
    )
    product_id: Optional[int]= Field(
        None,
        description="Used to specify which product ID the user wants data pertaining to. For example, '26', '48',  or '58' would be valid ways of using this argument."
    )    
    

class PostProcessParameters(BaseModel):
    """Inputs for post_process_data"""
    data_file: str = Field(
        ...,
        description=" This is a Json output to be displayed"
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