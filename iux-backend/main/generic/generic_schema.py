import os
import io
import requests
import json
import pandas as pd
import time
import random
import string
import datetime
from typing import Type
from typing import Optional, List
from pydantic import BaseModel, Field
from generic.generic_data_config import port
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from config.app_config import config
from generic.generic_e_types import DataHTTPException
from app_logger.logger import logger

def get_data_by_api(**kwargs):

    api_name = kwargs.pop('api_name')
    message_id = kwargs.pop('message_id')    
    url = config['agent']['api_url']
    endpoint = url + api_name
    args = {key.replace('_', '-'): value for key, value in kwargs.items()}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(endpoint, headers = headers, json = args)

    if response.status_code == 200:
        data = response.json()
        if 'data' in data:
            df = pd.DataFrame(data['data'])
        elif 'error-code' in data:
            error_message = {key.replace('-', '_'): value for key, value in data.items()}
            raise DataHTTPException(status_code=400, detail="Got an error from DATA API", error_message = error_message)
        else:
            error_message = {"error_code": "unknowndata_error", "error_message": "Corrupted data from DATA API."}
            raise DataHTTPException(status_code=400, detail="Fail to fetch data.", error_message = error_message)
        df = pd.DataFrame(data['data'])
        file_name = f'response_{message_id}.json'
# =============================================================================
#         for x in ['sales', 'margin', 'reg-price', 'list-cost']:
#             if x in df.columns:
#                 df[x] = (11 * df[x]).round(2)
#         for x in ['movement', 'visits']:
#             if x in df.columns:
#                 df[x] = 11 * df[x]
# =============================================================================
        data['data'] = df.to_dict(orient = 'records')
        logger.debug("writing file...")
        with open(file_name, 'w') as file:
            json.dump(data, file)    
        logger.debug("writing file is completed")
    else:
        error_message = {"error_code": "data_error", "error_message": "Failed to call DATA API"}
        raise DataHTTPException(status_code=400, detail="Fail to fetch data.", error_message = error_message)
    
    cols = df.columns.tolist()

    res = {}
    res['data_file'] = file_name
    res['columns'] = cols

    meta_keys = ['timeframe', 'locations', 'products']
    meta_data = {key: data[key] for key in meta_keys if key in data}
    logger.debug("writing meta file...")
    with open(f'meta-data_{message_id}.json', 'w') as file:
        json.dump(meta_data, file)
    logger.debug("writing meta file is completed")
    return json.dumps(res)



def transform_output_columns(df):
    column_name_mapping = {"item-code": "Item Code", "item-name" : "Item Name", 
                           "week-no" : "Week", "start-date" : "Start Date", 
                           "reg-price": "Reg Price", "list-cost": "List Cost",
                           "sales": "Sales", "margin": "Margin", 
                           "movement" : "Units", "margin-rate": "Margin %"}
    for old_name, new_name in column_name_mapping.items():
        if old_name in df.columns:
            df.rename(columns={old_name: new_name}, inplace=True)

# =============================================================================
# 
# =============================================================================

def post_process_data(data_file, action = 'min', cols = 'sales'):
    
# =============================================================================
#     kwargs = {'data_file':data_file, 'action':action, 'cols':cols}
#     with open('./logs/agents/data_access/log.txt', 'a') as logfile:        
#         logfile.write(pd.to_datetime(datetime.now()).strftime('%Y-%m-%d %I:%M:%S %p')
#                       + '\n    Tool: Post-Process\n    Args: ' + json.dumps(kwargs) + '\n\n')
# =============================================================================
    
    with open(data_file, 'r') as file:
        data = json.load(file)
    df = pd.DataFrame(data['data'])
    
    if isinstance(cols, str):
        cols = [word.strip() for word in cols.split(',')]

    columns_to_output = ["item-code", "item-name", "week-no", "start-date"]
    columns_to_output.extend(cols)

    add_cols = False
    if action == 'list':
        ## TODO: this is a hack to limit the number of items selected
        if len(df) >= 25:
            df = df.head(25)
            res = df
        #json_data = json.dumps(df[cols].to_json())
    elif action == 'max' or action == 'min':
        #numerical_cols = df[cols].select_dtypes(include=['number']).columns
        ### TODO: need more valiation here
        #num_col = numerical_cols[0]
        if action == 'max':
            res = df.loc[df[cols].idxmax()]
        else:
            non_zero_df = df.loc[df[cols[0]] != 0]
            logger.debug(f"non zero values {non_zero_df}")
            res = df.loc[non_zero_df[cols].idxmin()]
            
        #json_data = json.dumps(res.to_json())
    else:
        res =  df[cols].apply(action)
        add_cols = True
    
    
    
    res_df = res
    if add_cols:
        res_df = pd.DataFrame(res).T
        #res_df.columns = cols

    df_cols = list(res_df.columns.values)
    present_columns = [col for col in columns_to_output if col in df_cols]
    
    
    out_df = res_df.loc[:, present_columns]

    transform_output_columns(out_df)
    
    logger.debug(f"res_df = {out_df}, type = {type(out_df)}")
    res = {'type': 'table',  'tableData1' : out_df.to_dict(orient='records')}
    logger.debug(f"response after post processing: {res}")
        #json_data = json.dumps(res)

    return res


# =============================================================================
# 
# =============================================================================

def plot_data(data_file, type = 'line', metric_cols = 'sales',
              product_col = 'product-name', location_col = 'location-name'):
    
# =============================================================================
#     kwargs = {'data_file':data_file, 'type':type, 'metric_cols':metric_cols, 'product_col':product_col}
#     with open('./logs/agents/data_access/log.txt', 'a') as logfile:        
#         logfile.write(pd.to_datetime(datetime.now()).strftime('%Y-%m-%d %I:%M:%S %p')
#                       + '\n    Tool: Plot\n    Args: ' + json.dumps(kwargs) + '\n\n')
# =============================================================================
    with open(data_file, 'r') as file:
        data = json.load(file)
        
    if isinstance(metric_cols, str):
        metric_cols = [word.strip() for word in metric_cols.split(',')]
    
    if type == 'table':
        tableData1 = data.to_dict(orient='records')
        res = {'type': 'table',  'tableData1' : tableData1}
        print('Res')
        print(res)
    else:
        url = config['agent']['api_url'] + 'plotting'
        req_dict = {'data': data['data'],
                'type': type,
                'product-col': product_col,
                'metric-cols': metric_cols,
                'location-col': location_col}

        response = requests.post(url = url,
                        json = req_dict)
    
        if response.status_code == 200:
            res = response.json()
        else:
            error_message = {"error_code": "data_error", "error_message": "Failed to call Plotting API"}
            raise DataHTTPException(status_code=400, detail="Fail to fetch data.", error_message = error_message)

    #json_data = json.dumps(res)
    return res

# =============================================================================
# 
# =============================================================================

class APICallParameters(BaseModel):
    """Inputs for get_data_by_api"""
    api_name: str = Field(
        ...,
        description="APIs to call: 1. Movement API: it returns the weekly movement, sales, and margin data; 2. Price API: it returns the weekly regular prices; 3. Cost API: it returns the weekly list costs for all items; 4. Promotion API: it returns the weekly promotion types and sale prices.",
        enum=["movement", "price", "cost", "promotion"]
    )
    product_name: Optional[List[str]] = Field(
        None,
        description="Used to specify which product group the user wants data pertaining to. For example, ['Upper Respiratory'], ['OTC internal'],  or ['grocery'] would be valid ways of using this argument."
    )
    grouping_name: Optional[List[str]] = Field(
        None,
        description="Used to specify at which level user wants to group or collapse the data. For example, ['department'], ['major category'], ['category'], ['subcategory'], ['section'], ['segment'], ['item'], ['store']. It can have more than one grouping factors like, ['category', 'store']. If there is no grouping in the question, do NOT return any thing"
    )
    #item_list: Optional[List[str]] = Field(
        #None,
        #description="A list of items the user wants data pertaining to."
    #)
    location_name: Optional[List[str]] = Field(
        None,
        description="Used to specify the location the user wants data pertaining to. For example, ['Zone 620'] or ['online stores'] would be valid ways of using this argument."
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
    user_id: str = Field(
        None,
        description="This will be provided in the message. Copy exactly as is."
    )
    message_id: str = Field(
        None,
        description="This will be provided in the message. Copy exactly as is."
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
        description="Column or list of metric columns selected for plotting. Examples are ['sales'], ['movement'], ['cost', 'price'], etc"
    )
    product_col: str = Field(
        ...,
        description="Column of the product",
        enum=["product-name", "item-name"]
    )
    type: str = Field(
        ...,
        description= "The type of charts to plot",
        enum=["line", "bar", "table"]
    )
