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

    print(kwargs)

    api_name = kwargs.pop('api_name')
    print(api_name)

    if 'url' in kwargs:
        url = kwargs.pop('url')
    else:
        #url = 'http://127.0.0.1:49517/'
        url = config['agent']['api_url']
        #url = 'http://65.61.166.184:5001/'

    if 'user-id' in kwargs:
        user_id = kwargs.pop('user-id')
    else:
        user_id  = 'ejack'

    endpoint = url + api_name
    #converted_dict = {key.replace('-', '_'): value for key, value in kwargs.items()}
    converted_dict = {key.replace('_', '-'): value for key, value in kwargs.items()}
    if 'user-id' not in converted_dict:
        converted_dict['user-id'] = 'ejack'
    found_keyword = False
    headers = {'Content-Type': 'application/json'}
    #args =  {'user-id': '111'} 
    #print(converted_dict)
    #args =  {'user-id': user_id} 
    #converted_dict 
    #| {'user-id': user_id} 
    #print(args)
    #print(endpoint)
    #print(headers)
    print(converted_dict)
    response = requests.post(endpoint, headers = headers, json = converted_dict)
    print(response)
    print(response.json())
    print(type(response.json()))
    keywords = ["sorry", "apologize", "error","failed"]
    for keyword in range(len(keywords)):
        if keywords[keyword] in str(response.json()):
         found_keyword = True
   
    print(found_keyword)
    if found_keyword == False:
        data = response.json()
        print(data)
        timestamp = time.strftime('%Y%m%d%H%M%S')
        #print('Get Data By Api')
        #print(data)
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        file_name = f'response_{timestamp}_{random_string}.json'

        with open(file_name, 'w') as file:
            json.dump(data, file)
            #print(f'JSON data saved to {file_name}')
      
        print(type(data)) 
        #print(data)
        # print(type(data))
        #df = pd.DataFrame(data['data'])
        #data = json.loads(data)
        
        #data = json.dumps(data)
        data = json.loads(data)
        print(type(data))
        #data = json.dumps(data)
        #data = json.dumps(data)
        #inner_dict = data['data','Visits #','Visits %']
        # inner_dict = {
        #     'data': list(data['data'].values()),
        #     'Visits #': list(data['Visits #'].values()),
        #     'Visits %': list(data['Visits %'].values())
        # }
        print(type(data))
        ids = data['data'].keys()
    
        inner_dict = [
            {"ID": id, "data": data['data'][id], "Visits #": data['Visits #'][id], "Visits %": data['Visits %'][id]}
            for id in ids
        ]
        #inner_dict = data
        #print(inner_dict)
        #df = pd.DataFrame(inner_dict.items(), columns=['ID', 'Product Name','Visits #','Visits %'])
        df = pd.DataFrame(inner_dict)
        print(df)
        #df = pd.DataFrame(data['data'].items(), columns=['ID', 'Product Name'])
        cols = df.columns.tolist()
    
        res = {}
        res['data_file'] = file_name
        res['columns'] = cols
    
        # meta_keys = ['timeframe', 'locations', 'products']
        # meta_data = {key: data[key] for key in meta_keys if key in data}
        # with open('meta-data.json', 'w') as file:
        #     json.dump(meta_data, file)
    else:
        #print(f'Request failed with status code {response.status_code}')
        error_data = {
             "error_code": "Input Error",
             "error_message": "Looks like we were unable to fetch data from the given product name or item id. Could you please try rephrasing?",
             "detail": "Exception"
             }
        res = error_data

    return json.dumps(res)


def plot_data(data_file, type = 'line', metric_cols = 'sales', product_col = 'product-name'):
    #data_file = 'response_20230807164611_xzq8o2z3bs.json'
    with open(data_file, 'r') as file:
        data = json.load(file)
    
    #print(data)
    #data = json.dumps(data, indent=4)
    #print(data)
    #print(type(data))
    data = json.loads(data)
    #print(data)
    #print(type(data))
    # df = pd.DataFrame(data['data'])
    # df = df.astype({col: int for col in df.select_dtypes('int64').columns})
    print('Plot Data')
    
   
    
    #data = json.loads(data_file)
    #print(data)
    #df = pd.DataFrame(data['data'])
    df = pd.DataFrame(data)
    df.index.name = 'Index'  # You can set the index name as desired
    df.index = df.index.astype(int)  # Convert index to integers

    # Clean up the 'Visits #' column by removing commas and converting to integers
    #df['Visits #'] = df['Visits #'].str.replace(',', '').astype(int)

    # Clean up the 'Visits %' column by removing the percentage sign and converting to float
    #df['Visits %'] = df['Visits %'].str.rstrip('%').astype(float) 

    # if 'week-no' in df.columns:
    #     time_col = 'week-no'
    # elif 'period-no' in df.columns:
    #     time_col = 'period-no'
    # elif 'quarter-no' in df.columns:
    #     time_col = 'quarter-no'
    # else:
    #     time_col = 'cal-year'

    # if time_col != 'cal-year':
    #     time_cols = ['cal-year', time_col]
    # else:
    #     time_cols = ['cal-year']

    # print(time_col)
    # print(time_cols)

    # print(metric_cols)
    # if isinstance(metric_cols, str):
    #     metric_cols = [word.strip() for word in metric_cols.split(',')]
    # print(metric_cols)

    # id_cols = time_cols + [product_col]
    # all_cols = time_cols + [product_col] + metric_cols
    # print(all_cols)
    # df = df[all_cols]
    # ## drop dulicates
    # df = df.drop_duplicates(subset=id_cols)

    # time_col2 = '_'.join([time_col.replace('-', '_') for time_col in time_cols])
    # df[time_col2] = df['cal-year'].astype(str) + "_" + df[time_col].astype(str)
    # #unique_times = df[time_col2].unique().tolist()
    # unique_times = df[time_col].unique().tolist()

    # product_col2 = product_col.replace('-', '_')
    # print(product_col)
    # products = sorted(df[product_col].unique())

    if type == 'table':
        tableData1 = df.to_dict(orient='records')
        res = {'type': 'table',  'tableData1' : tableData1}
        print('Res')
        print(res)
        #res = json.dumps(res, ensure_ascii=False).replace('"', r'\"')
    #     options = { 'xaxis' : { time_col2 : unique_times}}
    #     if len(products) > 1 and  len(metric_cols) == 1:
    #         df_wide = df.pivot(index = time_col2, columns = product_col, values = metric_cols)
    #         cols = [f'{col[0]}_{col[1]}' for col in df_wide.columns]
    #         cols = [col.replace(' ', '_') for col in cols]
    #         df_wide.columns = cols
    #     elif len(products) == 1 and len(metric_cols) >= 1:
    #         df_wide = df[metric_cols]
    #         cols = df_wide.columns
    #     elif len(products) > 1 and len(metric_cols) > 1:
    #         df_wide = df.groupby(time_col2)[metric_cols].sum()
    #         cols = df_wide.columns
    #     series = [{'name': col, 'data': df_wide[col].tolist()} for col in cols]
    #     res = {'type': type,  'options' : options, 'series' : series}
    # elif type == 'bar':
    #     if len(products) == 1:
    #         options = { 'xaxis' : { time_col2 : unique_times}}
    #         df_wide = df[metric_cols]
    #         cols = df_wide.columns
    #     else:
    #         options = { 'xaxis' : { product_col2 : products}}
    #         df_wide = df.groupby(product_col)[metric_cols].sum()
    #         cols = df_wide.columns
    #     series = [{'name': col, 'data': df_wide[col].tolist()} for col in cols]
    #     res = {'type': type,  'options' : options, 'series' : series}
    #elif 
    else:
        print("chart type not supoorted !!!")
        res = {'Error': 'chart type not supported!'}
    json_data = res
    #json_data = json.dumps(res)
    #json_data = json.dumps(res, ensure_ascii=False).replace('"', r'\"')
    print('Json data')
    print(json_data)
    return json_data

#def post_process_data(data_file, action = 'mean', cols = 'sales', change = 'No'):
def post_process_data(data_file, action='mean', cols='sales'):
    with open(data_file, 'r') as file:
        data = json.load(file)
    print('Post Process Data')
    # print(data)
    # print(type(data))
    data = json.loads(data)

    # inner_dict = data['data']
    inner_dict = data
    # df = pd.DataFrame(inner_dict.items(), columns=['ID', 'Product Name'])
    # df = pd.DataFrame(data['data'])
    df = pd.DataFrame(inner_dict)
    df = df.rename(columns={"data": "Product Name"})
    print(df)
    # print(cols)
    if isinstance(cols, str):
        cols = [word.strip() for word in cols.split(',')]
    # print(cols)

    if action == 'list':
        items = df['Product Name'].unique().tolist()
        if len(items) <= 10:
            json_data = json.dumps(items)
        else:
            json_data = json.dumps(items[:10])
    else:
        res = df[cols].apply(action)
        json_data = json.dumps(res.to_json())

    return json_data


class APICallParameters(BaseModel):
    """Inputs for get_data_by_api"""
    api_name: str = Field(
        ...,
        description="APIs to call: 1. Movement API: it returns the weekly movement, sales, and margin data; 2. Price API: it returns the weekly regular prices; 3. Cost API: it returns the weekly list costs for all items; 4. Promotion API: it returns the weekly promotion types and sale prices;5. Affinity API: it returns which products are sold together or which products are bought together.",
        enum=["movement", "price", "cost", "promotion","affinity"]
    )
    product_name: Optional[List[str]] = Field(
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
    )

class PostProcessParameters(BaseModel):
    """Inputs for post_process_data"""
    data_file: str = Field(
        ...,
        description="Data file to be loaded to get the Pandas Data Frame."
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
        enum=["mean", "sum", "list","table"]
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