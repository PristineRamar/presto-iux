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

    print(kwargs)

    api_name = kwargs.pop('api_name')
    print(api_name)

    if 'url' in kwargs:
        url = kwargs.pop('url')
    else:
        url = config['agent']['api_url']

    if 'user-id' in kwargs:
        user_id = kwargs.pop('user-id')
    else:
        user_id  = 'ejack'
    #user_id  = 'ejack'
    endpoint = url + api_name
    #converted_dict = {key.replace('-', '_'): value for key, value in kwargs.items()}
    converted_dict = {key.replace('_', '-'): value for key, value in kwargs.items()}
    print(converted_dict)
    headers = {'Content-Type': 'application/json'}
    #args =  {'user-id': '111'} 
    args = converted_dict.copy()
    args.update({'user-id': user_id})
    #args =  converted_dict | {'user-id': user_id} 
    print(args)
    print(endpoint)
    args = json.dumps(args, indent=4)
    response = requests.post(endpoint, headers =  headers, json = args)

    if response.status_code == 200:
        print("success")
        data = response.content
        timestamp = time.strftime('%Y%m%d%H%M%S')
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        file_name = f'response_{timestamp}_{random_string}.json'
        data_str = data.decode('utf-8')
        with open(file_name, 'w') as file:
            json.dump(data_str, file)
            #print(f'JSON data saved to {file_name}')
    else:
        print(f'Request failed with status code {response.status_code}')
    data = json.loads( data )
    df = pd.DataFrame(data['data'])
    cols = df.columns.tolist()

    res = {}
    res['data_file'] = file_name
    res['columns'] = cols

    meta_keys = ['timeframe', 'locations', 'products']
    meta_data = {key: data[key] for key in meta_keys if key in data}
    with open('meta-data.json', 'w') as file:
        json.dump(meta_data, file)

    return json.dumps(res)

#def post_process_data(data_file, action = 'mean', cols = 'sales', change = 'No'):
def post_process_data(data_file, action = 'mean', cols = 'sales'):

    #data_file = 'response_20230801162717_eqlzmd9jel.json'

    with open(data_file, 'r') as file:
        data = json.load(file)
    df = pd.DataFrame(data['data'])

    print(cols)
    if isinstance(cols, str):
        cols = [word.strip() for word in cols.split(',')]
    print(cols)

    if action == 'list':
        ## TODO: this is a hack to limit the number of items selected
        if len(df) >= 25:
            df = df.head(25)
        json_data = json.dumps(df[cols].to_json())
    elif action == 'max' or action == 'min':
        numerical_cols = df[cols].select_dtypes(include=['number']).columns
        ### TODO: need more valiation here
        num_col = numerical_cols[0]
        if action == 'max':
            res = df.loc[df[num_col].idxmax()]
        else:
            res = df.loc[df[num_col].idxmin()]
        json_data = json.dumps(res.to_json())
    else:
        res = df[cols].apply(action)
        json_data = json.dumps(res.to_json())

    return json_data

def plot_data(data_file, type = 'line', metric_cols = 'sales', product_col = 'product-name', location_col = 'location-name'):

    #data_file = 'response_20230803140646_h86yf2vb5h.json'
    with open(data_file, 'r') as file:
        data = json.load(file)
    data = json.loads(data)
    # df = pd.DataFrame(data['data'])
    # df = df.astype({col: int for col in df.select_dtypes('int64').columns})
    data_dict = data['data']
    data_keys = list(data_dict.keys())
   
    out_data = {
    "type": type,
    "options": {
        "xaxis": {
            data_keys[0]: list(data_dict[data_keys[0]].values())
        }
    },
    "series": [
        {
            "name": "Price Index",
            "data":list(data_dict[data_keys[1]].values())
            }
        ]
    }
   
   
    return  out_data

class APICallParameters(BaseModel):
    """Inputs for get_data_by_api"""
    api_name: str = Field(
        ...,
        description="APIs to call: 1. Price Index API: it returns the price index the user wants api name pertain to. For example if the query is like create a table or graph of 'price index' or 'PI' for grocery for the last 2 quarters return the string as priceindex",
        enum=["priceindex"]
    )
    child_prod_level: Optional[List[str]] = Field( None,
       
        description="Used to specify the any product level under a product name or specifying any product levels only like 'All departments','All categories' . the user wants data pertaining to. For example,'Department','Major Category', 'Category' or 'Sub category' or 'Segment' or 'Item' would be valid ways of using this argument."
       
    )
    cal_type:  Optional[List[str]] = Field(
        None,
       
        description="Used to specify the calendar types. the user wants data pertaining to. For example, 'Q' is valid for 'Quarter',  'W' is valid for Weeks, 'P' is valid for 'Periods'. apart from 'Q' or 'P' or 'W' should not be used. for instance, if user is asking 'Last quarter' this argument Should be 'Q', or 'Last 2 weeks' this argument Should be 'W' "
        
    )
    
    product_name: Optional[List[str]] = Field(
        None,
        description="Used to specify which product group the user wants data pertaining to. For example, 'Upper Respiratory', 'OTC internal',  or 'grocery' would be valid ways of using this argument.Product levels like 'Departments', 'Category', 'All'..etc are not valid for this argument"
    )
  
    comp_tier: Optional[List[str]] = Field(
        None,
        description= "Used to specify Competitor Tier the user wants data pertaining to. For example, 'Primary', 'Secondary' would be valid ways of using this argument"
        
    )
    comp_name: Optional[List[str]] = Field(
       None,
        description= "Used to specify which Competitor the user wants data pertaining to. For example, 'Wallgreens', 'CVC' would be valid ways of using this argument. The types like 'Primary', 'Secondary' cannot be the competitor name"
        
    )
    
    comp_city: Optional[List[str]] = Field(
       None,
        description= "Used to specify which City of the Competitor the user wants data pertaining to. For example, 'Seattle', 'Dover' would be valid ways of using this argument"
        
    )
    comp_addr: Optional[List[str]] = Field(
      None,
       description= "Used to specify The address of the Competitor the user wants data pertaining to. For example, '5190 Library Rd ', '1801 York Rd' would be valid ways of using this argument"
       
     )
    product_agg: Optional[List[str]] = Field(
        None,
        description= "do this if you are 100% sure: A flag to indicate if the query is about aggregation or summarization or averaging at product level. This flag only applies when user says about aggregation levels. if aggregation at product level the flag should be 'Y' else if they need such as  'aggregate at calendar level'  or 'aggregate at week level' or 'aggregatd at zone level' or 'aggregatd at quarter level' the should be 'N' ",
        enum=[ "Y", "N"]
    )
    location_name: Optional[List[str]] = Field(
       None,
        description="Used to specify the location the user wants data pertaining to. For example, 'Zone 620' or 'online stores' would be valid ways of using this argument. "
    )
    loc_agg: Optional[List[str]] = Field(
       None,
        description= "do this if you are 100% sure: A flag to indicate if the query is about aggregation or summarization or averaging at location level. This flag only applies when user says about aggregation levels. if aggregation at location level or zone level the flag should be 'Y' else 'N'for example 'aggregate at location level' the flag is 'Y'. for the context 'aggregate at week level' or 'aggregatd at product level' the should be 'N' ",
        enum=[ "Y", "N"]
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
    cal_agg: Optional[List[str]] = Field(
        None,
        description= "do this if you are 100% sure: A flag to indicate if the query is about aggregation or summarization or averaging at time frame level. This flag only applies when user says about aggregation levels. if aggregation at week level or calendar level or date wise the flag should be 'Y' else 'N'for example 'aggregate at week level or calendar or date wise' the flag is 'Y' else 'aggregate at location or zone level' or 'aggregatd at product level' the would be 'N' ",
        enum=[ "Y", "N"]
    )
    
    pi_type:  Optional[List[str]] = Field(
       None,
        description="Used to specify the price index types. the user wants data pertaining to. For example, 'S' is valid for 'Simple Index', 'Reg price index' and 'Reg Index' and 'B' is valid for 'Blended Index', 'promotion idex' or 'promo index'. apart from 'S' or 'B' should not be used",
        enum=["S", "B"]
    )
    weighted_by:  Optional[List[str]] = Field(
      None,
        description="Used to specify whether price index weighted by 1. movement 2.margin 3.revenue 4. 13 week movement  5.visit. use 'M' for movement, 'MR' for margin,'R' for revenue, 'M13' for 13 week movement, 'V' for visit",
       
        enum=["M", "MR", "R","M13","V"]
    )
   

class PostProcessParameters(BaseModel):
    """Inputs for post_process_data"""
    data_file: str = Field(
        ...,
        description="Data file to be loaded to get the Pandas Data Frame."
    )
    cols: List[str] = Field(
        ...,
        description="Column or list of columns selected for post processing. Examples are metric columns like sales, movement, cost, price, etc, NEVER put the label columns in this list"
    )
    action: str = Field(
        ...,
        description= "A function to be applied to the Data Frame",
        #enum=["mean", "sum", "detect-change", "list"]
        #enum=["mean", "sum", "detect-change"]
        enum=["mean", "sum", "list"]
    )

class PlotDataParameters(BaseModel):
    """Inputs for plot_data"""
    data_file: str = Field(
        ...,
        description="Data file to be loaded to get the Pandas Data Frame."
    )
    metric_cols: List[str] = Field(
        ...,
        description="Column or list of metric columns selected for plotting. Examples are sales, movement, cost, price, etc"
    )
    product_col: str = Field(
        ...,
        description="The column name of the product or item. Examples are product_name or item_name"
    )
    type: str = Field(
        ...,
        description= "The type of charts to plot",
        enum=["line", "bar", "table"]
    )
