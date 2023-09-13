# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 11:19:18 2023

@author: Dan
"""

import requests
import pandas as pd
import numpy as np
import cx_Oracle
import time

from rapidfuzz.process import extractOne
from rapidfuzz.fuzz import QRatio
from price_index.price_index_data_functions_common import (cal_lookup, sanitize_cal_input,
                                   parse_prod_request, parse_loc_request,
                                   prod_hier, product_data)
from price_index.price_index_data_config import (data_url, username, password, dbname, n_responses)

from datetime import datetime
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# =============================================================================
# 
# =============================================================================

def call_api(api_path, locs, prods, cal, active, start_week = None):

    responses = []
    start = time.time()
    for l in locs:
        for z in locs[l]:
            for p in prods:
                if p > 1:
                    for w in prods[p]:  
                        temp = prod_hier(product_id = w, product_level = p, detail_level = 1, active = active)
                        if p >= 2:
                            response = requests.post(data_url + api_path,
                                                     json = {"locationLevelId": int(l),      
                                                             "locationId": int(z), 
                                                             "startDate": start_week.strftime('%m/%d/%Y') if start_week else cal['end-date'].min().strftime('%m/%d/%Y'), 
                                                             "endDate": cal['end-date'].max().strftime('%m/%d/%Y'),   
                                                             "calType": "W",            
                                                             "fiscalOrAdCalendar": "B",
                                                             "productId":int(w),
                                                             "productLevelId":int(p)})
                        elif p == 1.5:
                            response = requests.post(data_url + api_path,
                                                     json = {"locationLevelId": int(l),      
                                                             "locationId": int(z), 
                                                             "startDate": start_week.strftime('%m/%d/%Y') if start_week else cal['end-date'].min().strftime('%m/%d/%Y'),
                                                             "endDate": cal['end-date'].max().strftime('%m/%d/%Y'),   
                                                             "calType": "W",            
                                                             "fiscalOrAdCalendar": "B",
                                                             "itemCodes":[int(x) for x in temp['item-code']]})
                        response = pd.DataFrame(response.json())
                        if response.empty:
                            continue
                        response = response.rename(columns = {'itemCode':'item-code'})
                        response = temp.loc[:, ['item-name', 'item-code']].merge(response, how = 'inner', on = 'item-code')
                        response['product-level'] = p
                        response['product-id'] = w
                        responses.append(response)
                elif p == 1:
                    temp = prod_hier(product_id = prods[p], product_level = p, detail_level = 1, active = active)
                    response = requests.post(data_url + api_path,
                                             json = {"locationLevelId": int(l),      
                                                     "locationId": int(z), 
                                                     "startDate": start_week.strftime('%m/%d/%Y') if start_week else cal['end-date'].min().strftime('%m/%d/%Y'),
                                                     "endDate": cal['end-date'].max().strftime('%m/%d/%Y'),   
                                                     "calType": "W",            
                                                     "fiscalOrAdCalendar": "B",
                                                     "itemCodes":[int(x) for x in temp['item-code']]})
                    response = pd.DataFrame(response.json())
                    if response.empty:
                        continue
                    response = response.rename(columns = {'itemCode':'item-code'})
                    response = temp.loc[:, ['item-name', 'item-code']].merge(response, how = 'inner', on = 'item-code')
                    response['product-level'] = p
                    response['product-id'] = response['item-code']
                    responses.append(response)
    response = pd.concat(responses, ignore_index = True)
    end = time.time()
    print('Time taken: {} seconds'.format(round(end - start, 2)))
    return response

# =============================================================================
# 
# =============================================================================

def cal_logic(cal_year, quarter, period, week, day, start_date, end_date, calendar_id):
    if start_date is not None or end_date is not None or calendar_id is not None:
        return cal_year, quarter, period, week, day, start_date, end_date, calendar_id
    if cal_year is None:
        if quarter is None and period is None and week is None and day is None:
            quarter = 'current'
        cal_year, quarter, period, week, day = sanitize_cal_input(cal_year, quarter, period, week, day)
        if type(quarter) == int or type(quarter) == list:
            cal_year = 'current'
        if type(period) == int or type(period) == list:
            cal_year = 'current'
        if type(week) == int or type(week) == list:
            cal_year = 'current'
        if type(day) == int or type(day) == list:
            cal_year = 'current'
    return cal_year, quarter, period, week, day, start_date, end_date, calendar_id

# =============================================================================
# 
# =============================================================================

def catch_empty_list(l):
    if type(l) == list and l == []:
        return None
    else:
        return l

# =============================================================================
# 
# =============================================================================

def sanitize_list(x):
    if type(x) == list and len(x) > 0:
        return x[0]
    return x  

# =============================================================================
# 
# =============================================================================    


def process_variable(var):
    
    if isinstance(var, list):
       
        if len(var) == 0:
            
            return None
        else:
            return var[0]
    else:
        return var
def reportgen(product_name = None, product_id = None, product_level = None, 
              child_prod_level = None, product_agg = 'N', item_list = None,
              active = 'Y', group_name = None,
             location_name = None, location_id = None, location_level = None, loc_agg = 'N', 
             cal_year = None, quarter =None, period = None, week = None, day = None,
             start_date = None, end_date = None, calendar_id = None, 
             cal_type = 'Q', user_id = None,cal_agg = 'N',pi_type = "S",weighted_by = None,
             comp_city = None,
             comp_addr = None,
             comp_name = None,
             comp_tier = None): 
    # if (comp_city is not None) or (comp_addr is not None) or  (comp_name is not None) or (comp_tier is not None):
    #     comp_df = comp_parser(location_name  , comp_city,
    #                                comp_addr , comp_name, comp_tier)
    #     location_id = comp_df['LOCATION_ID'].unique()
    #     location_level = 6
    #     comp_str_id = comp_df['COMP_STR_ID'].unique()
    
    cal_type = process_variable(cal_type)
    print(cal_type)
    quarter = process_variable (quarter)
    print(quarter)
    product_name = process_variable(product_name)
    product_id = process_variable(product_id)
    product_level = process_variable(product_level) 
    child_prod_level = process_variable(child_prod_level) 
    product_agg = process_variable(product_agg) 
    item_list = process_variable(item_list) 
    active =  process_variable(active)
    group_name =  process_variable(group_name)
    location_name = process_variable(location_name)
    location_id = process_variable(location_id)
    location_level = process_variable (location_level)
    loc_agg = process_variable (loc_agg)
    cal_year =  process_variable (cal_year)
    
    period = process_variable (period)
    week =process_variable(week) 
    day = process_variable (day)
    # start_date = process_variable (start_date)
    # end_date = process_variable (end_date)
    calendar_id = process_variable(calendar_id)
   
    user_id = process_variable(user_id)
    cal_agg = process_variable(cal_agg)
    pi_type =process_variable(pi_type)
    weighted_by = process_variable(weighted_by)           
    comp_city = process_variable(comp_city)             
    comp_addr = process_variable(comp_addr) 
    comp_name = process_variable(comp_name) 
    comp_tier = process_variable(comp_tier) 
    if product_agg is None:
        product_agg = 'N'
    if active is None:
        active = 'Y'
    if loc_agg is None:
        loc_agg = 'N'
    if cal_type is None:
        cal_type = 'Q'
    if cal_agg is None:
        cal_agg = 'N'
    if  pi_type is None:
        pi_type = "S"
    
    
    if  cal_type == 'Q' and quarter is None:
        quarter = 'Last 1'
    if  cal_type == 'W' and week is None:
        week = 'Last 1'
    if  cal_type == 'P' and period is None:
        period = 'Last 1'  
    
    if  cal_type is None and quarter is not None:
        cal_type = 'Q'
    if  cal_type is None and week is not None:
        cal_type = 'W'
    if  cal_type is None and period is not None:
        period = 'P'     
    
    cal_year, quarter, period, week, day, start_date, end_date, calendar_id = cal_logic(cal_year, quarter, period, week, day, start_date, end_date, calendar_id)
    if start_date is not None:
       if len(start_date) == 0:
           start_date = None
       if len(end_date) == 0:
           end_date = None
    if product_name is not None:
        if product_name in ['All','all','any']:
            product_name = None
    
    cal = cal_lookup(cal_year, quarter, period, week, day,
                     start_date, end_date, calendar_id, cal_type)
    if  child_prod_level is not None:
        child_prod_level = product_level_identifier(child_prod_level)
    if cal.empty:
        raise ValueError('timeframe')
        
    last_week = cal_lookup(week = 'last 1')
    start_date = min(cal['start-date'].min(), last_week['start-date'].min())
    start_date = start_date.strftime("%Y-%m-%d")
    end_date = max(cal['end-date'])
    end_date = end_date.strftime("%Y-%m-%d")
    location_name = catch_empty_list(location_name)    
    if location_name is not None:
        locations = parse_loc_request(location_name, location_id, location_level, active) 
        location_level = locations.iloc[0,1]
        location_id = locations.iloc[0,0]
        loc_names = list(locations['location-name'].drop_duplicates())
        locs = {l:[int(x) for x in locations.loc[locations['location-level'] == l, 'location-id']] for l in locations['location-level'].unique()}
    else:
        location_level = None
        location_id = None
   
    
    if (location_level == 1 and location_id == 52):
        location_level = None 
        location_id = None
    product_name = catch_empty_list(product_name)
    
    products = parse_prod_request(product_name, product_id, product_level,
                               user_id, active)
    if product_name is not None:
        product_name = products.iloc[0,2]
    

    if products.empty:
        raise ValueError('product')
        
    if (products['authorized'] == False).all():
        raise ValueError('authorization')
        
    products = products.loc[products['authorized']]
        
    prod_names = list(products['product-name'].drop_duplicates())
    prods = {p:[int(x) for x in products.loc[products['product-level'] == p, 'product-id']] for p in products['product-level'].unique()}
    #1. Get PI for all products at a product level
    product_id = int(products.iloc[0,0])
    product_level = int(products.iloc[0,1])
    if ((product_level == 99) & (product_id == 9491)):
        product_id =None
        product_level = None
    if (location_level == 1 and location_id == 52):
        location_level = None 
        location_id = None
    if (product_level is None and child_prod_level is  None) :
        prod_id_cat, child_prod_cat_name, child_prod_id_cat = child_prod_query_string(product_level,child_prod_level)
        result = prod_level_query(product_id,prod_id_cat, child_prod_cat_name, child_prod_id_cat,start_date,end_date, location_id,comp_city,
         comp_addr,
         comp_name,
         comp_tier)  
    #2. Get PI for all products at a child_product level under a product_level
    #PI Report  at any calendar range for a child_product level under a product_level
    if  (product_level is not None and child_prod_level is None) or  (product_level is not None and child_prod_level is not None) or (product_level is None and child_prod_level is not None):
        prod_id_cat, child_prod_cat_name, child_prod_id_cat = child_prod_query_string(child_prod_level,product_level)
        result = prod_level_query(product_id,prod_id_cat, child_prod_cat_name, child_prod_id_cat,start_date,end_date,location_id, comp_city,
         comp_addr,
         comp_name,
         comp_tier)  
    
    # Aggregation levels
    if (product_agg == 'Y') or (product_agg == 'N' and loc_agg == 'N' and cal_agg == 'N'):
        result_grp = result.groupby("PRODUCT_NAME")
    if loc_agg == 'Y':
        result_grp = result.groupby("LOCATION_NAME")
    if cal_agg == 'Y':
        result_grp = result.groupby("START_DATE")
   
   # Index mean types
    if pi_type == 'S' and weighted_by is None : 
        df = result_grp["SIMPLE_INDEX"].mean()
    elif pi_type == 'B' and weighted_by is None:
        df = result_grp["BLENDED_INDEX"].mean()
    elif pi_type == 'S'  and weighted_by == 'M':
        df = result_grp["W_MOVEMENT_IX_REG"].mean()
    elif pi_type == 'B'  and weighted_by == 'M':
        df = result_grp["W_MOVEMENT_IX_PROMO"].mean()
    elif pi_type == 'S'  and weighted_by == 'MR':
        df = result_grp["W_MARGIN_IX_REG"].mean()
    elif pi_type == 'B'  and weighted_by == 'MR':
        df = result_grp["W_MARGIN_IX_PROMO"].mean()
    elif pi_type == 'S'  and weighted_by == 'R':
        df = result_grp["W_REVENUE_IX_REG"].mean()
    elif pi_type == 'B'  and weighted_by == 'R':
        df = result_grp["W_REVENUE_IX_PROMO"].mean()
    elif pi_type == 'S'  and weighted_by == 'M13':
        df = result_grp["W_13WEEK_MOVEMENT_IX_REG"].mean()
    elif pi_type == 'B'  and weighted_by == 'M13':
        df = result_grp["W_13WEEK_MOVEMENT_IX_PROMO"].mean()
    elif pi_type == 'S'  and weighted_by == 'V':
        df = result_grp["W_VISIT_IX_REG"].mean()
    elif pi_type == 'B'  and weighted_by == 'V':
        df = result_grp["W_VISIT_IX_PROMO"].mean()
    else:
        df = result_grp["SIMPLE_INDEX"].mean()
    df = df.round(2)
    df = pd.DataFrame(df)
    idx_dtype = pd.api.types.is_datetime64_any_dtype(df.index)
    if idx_dtype == True: 
        df.index = df.index.strftime('%Y-%m-%d')
    df.reset_index(inplace=True)
    json_data = df.to_json()
    meta_data = {
        "timeframe": start_date + " - " + end_date,
        "locations": ["Zone"],
        "products": [product_name]
      }
    
    return meta_data,json_data



def child_prod_query_string(child_prod_level, product_level_id = None):
    child_prod_cat_name  = ''
    child_prod_id_cat = ''
    prod_id_cat = ''
    if product_level_id != 1 and child_prod_level != None: 
        
        if product_level_id == 5:
            prod_id_cat = 'DEPARTMENT_ID' 
            if child_prod_level == 4: 
                child_prod_cat_name  = 'CATEGORY_NAME'
                child_prod_id_cat = 'CATEGORY_ID'
            elif child_prod_level == 3: 
                child_prod_cat_name  = 'SUB_CATEGORY_NAME'
                child_prod_id_cat = 'SUB_CATEGORY_ID'
            elif child_prod_level == 2: 
                child_prod_cat_name  = 'SEGMENT_NAME'
                child_prod_id_cat = 'SEGMENT_ID'
            elif child_prod_level == 1: 
                child_prod_cat_name  = 'ITEM_NAME'
                child_prod_id_cat = 'ITEM_CODE'
        if product_level_id == 4:
            prod_id_cat = 'CATEGORY_ID' 
            if child_prod_level == 3: 
                child_prod_cat_name  = 'SUB_CATEGORY_NAME'
                child_prod_id_cat = 'SUB_CATEGORY_ID'
            elif child_prod_level == 2: 
                child_prod_cat_name  = 'SEGMENT_NAME'
                child_prod_id_cat = 'SEGMENT_ID'
            elif child_prod_level == 1: 
                child_prod_cat_name  = 'ITEM_NAME'
                child_prod_id_cat = 'ITEM_CODE' 
        if product_level_id == 3:
            prod_id_cat = 'SUB_CATEGORY_ID' 
            if child_prod_level == 2: 
                child_prod_cat_name = 'SEGMENT_NAME'
                child_prod_id_cat = 'SEGMENT_ID'
            elif child_prod_level == 1: 
                child_prod_cat_name  = 'ITEM_NAME'
                child_prod_id_cat = 'ITEM_CODE' 
    if product_level_id != 1 and child_prod_level == None: 
        prod_id_cat = None
        if product_level_id == 5:
            
            child_prod_cat_name  = 'CATEGORY_NAME'
            child_prod_id_cat = 'CATEGORY_ID'
            
        if product_level_id == 4:
           
            child_prod_cat_name  = 'SUB_CATEGORY_NAME'
            child_prod_id_cat = 'SUB_CATEGORY_ID'
           
        if product_level_id == 3:
             
           
             child_prod_cat_name = 'SEGMENT_NAME'
             child_prod_id_cat = 'SEGMENT_ID'
            
        if product_level_id == 2:
            
             child_prod_cat_name  = 'ITEM_NAME'
             child_prod_id_cat = 'ITEM_CODE'  
    if product_level_id == 1 and child_prod_level == None:
        prod_id_cat = None
        child_prod_cat_name  = 'ITEM_NAME'
        child_prod_id_cat = 'ITEM_CODE' 
    if product_level_id == None and child_prod_level == None:
        prod_id_cat = None
        child_prod_cat_name  = 'CATEGORY_NAME'
        child_prod_id_cat = 'CATEGORY_ID'
    if product_level_id == None and child_prod_level != None: 
         prod_id_cat = None
         if child_prod_level == 5:
             
             child_prod_cat_name  = 'DEPARTMENT_NAME'
             child_prod_id_cat = 'DEPARTMENT_ID'
             
         if child_prod_level == 4:
             
             child_prod_cat_name  = 'CATEGORY_NAME'
             child_prod_id_cat = 'CATEGORY_ID'
             
         if child_prod_level == 3:
            
             child_prod_cat_name  = 'SUB_CATEGORY_NAME'
             child_prod_id_cat = 'SUB_CATEGORY_ID'
            
         if child_prod_level == 2:
              
            
              child_prod_cat_name = 'SEGMENT_NAME'
              child_prod_id_cat = 'SEGMENT_ID'
             
         if child_prod_level == 1:
             
              child_prod_cat_name  = 'ITEM_NAME'
              child_prod_id_cat = 'ITEM_CODE'  
              
    return prod_id_cat, child_prod_cat_name, child_prod_id_cat 
    


def prod_level_query(product_id,prod_id_cat, child_prod_cat_name, 
                     child_prod_id_cat,start_date,end_date, location_id,  comp_city,
                      comp_addr,
                      comp_name,
                      comp_tier):
    count_non_none, comp_col,name_comp,comp_col1,name_comp1 = comp_parser( comp_city,comp_addr,comp_name, comp_tier)
    if prod_id_cat !=None and product_id != None:
        prod_fil = "and {}={}".format(prod_id_cat,product_id)
    else:
        prod_fil = ''
    
    
    query = ''
    if child_prod_id_cat != 'ITEM_CODE': 
  
        query = ''' WITH PI_TABLE AS (SELECT pid.product_id,
                                        pid.product_level_id,
                                        PS.BASE_LOCATION_LEVEL_ID, 
                                        PS.BASE_LOCATION_ID,
                                        ps.start_date,
                                        PS.COMP_LOCATION_ID COMP_STR_ID,
                                        pid.simple_index,PID.blended_index,
                                        PID.W_MOVEMENT_IX_REG,
                                        PID.W_MOVEMENT_IX_PROMO, 
                                        PID.W_MARGIN_IX_REG,
                                        PID.W_MARGIN_IX_PROMO,  
                                        PID.W_REVENUE_IX_REG,
                                        PID.W_REVENUE_IX_PROMO,
                                            W_13WEEK_MOVEMENT_IX_REG,
                                            W_13WEEK_MOVEMENT_IX_PROMO,
                                            W_VISIT_IX_REG,
                                            W_VISIT_IX_PROMO 
 
                            from pi_selection_criteria ps
                            left join price_index_data pid
                            on 
                            pid.analysis_id = ps.analysis_id
                            where 
                            pid.product_id in (SELECT DISTINCT({}) FROM
                                               ITEM_DETAILS_VIEW WHERE ACTIVE_INDICATOR = 'Y' {})   and 
                            ps.start_date >= to_date('{}','YYYY-MM-DD')
                            and ps.start_date <= to_date('{}','YYYY-MM-DD')),
                PROD_DATA AS (                
                    select DISTINCT {}, {} FROM ITEM_DETAILS_VIEW WHERE ACTIVE_INDICATOR = 'Y'),
                 
                COMP_DATA AS (SELECT RPZ.PRICE_ZONE_ID LOCATION_ID,RPZ.ZONE_NUM LOCATION_NAME,PRIMARY_COMP_STR_ID COMP_STR_ID,'Primary' as COMP_TIER,CS.NAME COMP_NAME,CS.ADDR_LINE1,CS.CITY  FROM RETAIL_PRICE_ZONE RPZ LEFT JOIN COMPETITOR_STORE CS
                                ON 
                            RPZ.PRIMARY_COMP_STR_ID = CS.COMP_STR_ID
                            WHERE RPZ.PRIMARY_COMP_STR_ID IS NOT NULL AND RPZ.ACTIVE_INDICATOR = 'Y'
                            UNION ALL
                            SELECT RPZ.PRICE_ZONE_ID LOCATION_ID,RPZ.ZONE_NUM LOCATION_NAME,SECONDARY_COMP_STR_ID_1 COMP_STR_ID,'Secondary' as COMP_TIER,CS.NAME COMP_NAME,CS.ADDR_LINE1,CS.CITY  FROM RETAIL_PRICE_ZONE RPZ LEFT JOIN COMPETITOR_STORE CS
                                ON 
                            RPZ.SECONDARY_COMP_STR_ID_1 = CS.COMP_STR_ID
                            WHERE SECONDARY_COMP_STR_ID_1 IS NOT NULL AND  RPZ.ACTIVE_INDICATOR = 'Y' )


            SELECT  product_id, {},
                product_level_id,
                    BASE_LOCATION_LEVEL_ID, 
                    BASE_LOCATION_ID,
                    CD.LOCATION_NAME,CD.COMP_STR_ID,CD.COMP_TIER,COMP_NAME,CD.ADDR_LINE1,CD.CITY,
                    start_date,
                    simple_index, blended_index,
                    W_MOVEMENT_IX_REG,
                    W_MOVEMENT_IX_PROMO, 
                    W_MARGIN_IX_REG,
                    W_MARGIN_IX_PROMO,  
                    W_REVENUE_IX_REG,
                    W_REVENUE_IX_PROMO,
                    W_13WEEK_MOVEMENT_IX_REG,
                    W_13WEEK_MOVEMENT_IX_PROMO,
                    W_VISIT_IX_REG,
                    W_VISIT_IX_PROMO 
                    FROM PI_TABLE PI LEFT JOIN PROD_DATA PD
                    ON
                    PI.PRODUCT_ID = PD.{}
                    LEFT JOIN COMP_DATA CD
                   ON PI.COMP_STR_ID  = CD.COMP_STR_ID
                   
                  AND PI.BASE_LOCATION_ID = CD.LOCATION_ID
                    '''.format(child_prod_id_cat,
                    prod_fil,start_date,end_date,child_prod_id_cat, child_prod_cat_name,
                    child_prod_cat_name,child_prod_id_cat)
    else:
        query = ''' WITH PI_TABLE AS (SELECT
        PID.ITEM_CODE AS PRODUCT_ID,
        1 AS product_level_id,
        PS.BASE_LOCATION_LEVEL_ID,
        PS.BASE_LOCATION_ID,PS.COMP_LOCATION_ID COMP_STR_ID,
        PS.START_DATE,
        PID.REGULAR AS simple_index,
        PID.PROMOTIONAL AS blended_index,
        (PID.ITEM_MOVEMENT * COMP_STR_REG) / (BASE_STR_REG * PID.ITEM_MOVEMENT) * 100 AS W_MOVEMENT_IX_REG,
        (PID.ITEM_MOVEMENT * (CASE WHEN COMP_STR_SALE = 0 THEN COMP_STR_REG ELSE COMP_STR_SALE END) /
        (CASE WHEN BASE_STR_SALE = 0 THEN BASE_STR_REG ELSE BASE_STR_SALE END)) * 100 AS W_MOVEMENT_IX_PROMO,
        100 AS W_MARGIN_IX_REG,
        100 AS W_MARGIN_IX_PROMO,
        (PID.ITEM_REVENUE * COMP_STR_REG) / (BASE_STR_REG * PID.ITEM_REVENUE) * 100 AS W_REVENUE_IX_REG,
        (PID.ITEM_REVENUE * (CASE WHEN COMP_STR_SALE = 0 THEN COMP_STR_REG ELSE COMP_STR_SALE END) /
        (CASE WHEN BASE_STR_SALE = 0 THEN BASE_STR_REG ELSE BASE_STR_SALE END)) * 100 AS W_REVENUE_IX_PROMO,
        (PID.ITEM_MOVEMENT_13WEEK * COMP_STR_REG) / (BASE_STR_REG * PID.ITEM_MOVEMENT_13WEEK) * 100 AS W_13WEEK_MOVEMENT_IX_REG,
        (PID.ITEM_MOVEMENT_13WEEK * (CASE WHEN COMP_STR_SALE = 0 THEN COMP_STR_REG ELSE COMP_STR_SALE END ) /
        (CASE WHEN BASE_STR_SALE = 0 THEN BASE_STR_REG ELSE BASE_STR_SALE END)*PID.ITEM_MOVEMENT_13WEEK ) * 100 AS W_13WEEK_MOVEMENT_IX_PROMO,
        100 AS W_VISIT_IX_REG,
        100 AS W_VISIT_IX_PROMO
        FROM
                pi_selection_criteria PS
                LEFT JOIN
                price_index_item_data PID ON PID.ANALYSIS_ID = PS.ANALYSIS_ID
                WHERE
                PID.BASE_STR_REG != 0 AND  PID.ITEM_MOVEMENT_13WEEK !=0 AND  PID.ITEM_MOVEMENT !=0 AND PID.ITEM_REVENUE != 0 AND
                           
                            pid.ITEM_CODE in (SELECT DISTINCT({}) FROM
                                               ITEM_DETAILS_VIEW WHERE ACTIVE_INDICATOR = 'Y' {})   and 
                            ps.start_date >= to_date('{}','YYYY-MM-DD')
                            and ps.start_date <= to_date('{}','YYYY-MM-DD')),
                PROD_DATA AS (                
                    select DISTINCT {}, {} FROM ITEM_DETAILS_VIEW WHERE ACTIVE_INDICATOR = 'Y'),
                COMP_DATA AS (SELECT RPZ.PRICE_ZONE_ID LOCATION_ID,RPZ.ZONE_NUM LOCATION_NAME,PRIMARY_COMP_STR_ID COMP_STR_ID,'Primary' as COMP_TIER,CS.NAME COMP_NAME,CS.ADDR_LINE1,CS.CITY  FROM RETAIL_PRICE_ZONE RPZ LEFT JOIN COMPETITOR_STORE CS
                                ON 
                            RPZ.PRIMARY_COMP_STR_ID = CS.COMP_STR_ID
                            WHERE RPZ.PRIMARY_COMP_STR_ID IS NOT NULL AND RPZ.ACTIVE_INDICATOR = 'Y'
                            UNION ALL
                            SELECT RPZ.PRICE_ZONE_ID LOCATION_ID,RPZ.ZONE_NUM LOCATION_NAME,SECONDARY_COMP_STR_ID_1 COMP_STR_ID,'Secondary' as COMP_TIER,CS.NAME COMP_NAME,CS.ADDR_LINE1,CS.CITY  FROM RETAIL_PRICE_ZONE RPZ LEFT JOIN COMPETITOR_STORE CS
                                ON 
                            RPZ.SECONDARY_COMP_STR_ID_1 = CS.COMP_STR_ID
                            WHERE SECONDARY_COMP_STR_ID_1 IS NOT NULL AND  RPZ.ACTIVE_INDICATOR = 'Y' )

            SELECT  product_id, {},
                product_level_id,
                    BASE_LOCATION_LEVEL_ID, 
                    BASE_LOCATION_ID,
                    PI.LOCATION_NAME,CD.COMP_STR_ID,CD.COMP_TIER,COMP_NAME,CD.ADDR_LINE1,CD.CITY,
                    start_date,
                    simple_index, blended_index,
                    W_MOVEMENT_IX_REG,
                    W_MOVEMENT_IX_PROMO, 
                    W_MARGIN_IX_REG,
                    W_MARGIN_IX_PROMO,  
                    W_REVENUE_IX_REG,
                    W_REVENUE_IX_PROMO,
                    W_13WEEK_MOVEMENT_IX_REG,
                    W_13WEEK_MOVEMENT_IX_PROMO,
                    W_VISIT_IX_REG,
                    W_VISIT_IX_PROMO 
                    FROM PI_TABLE PI LEFT JOIN PROD_DATA PD
                    ON
                    PI.PRODUCT_ID = PD.{}
                    LEFT JOIN COMP_DATA CD
                     ON ON PI.COMP_STR_ID  = CD.COMP_STR_ID 
                     AND PI.BASE_LOCATION_ID = CD.LOCATION_ID'''.format(child_prod_id_cat,
                    prod_fil,start_date,end_date,child_prod_id_cat, child_prod_cat_name,
                    child_prod_cat_name,child_prod_id_cat)
    print(query)
    connection = cx_Oracle.connect(username , password,dbname )
    cursor = connection.cursor()
    cursor.execute( query)
    result = cursor.fetchall()
    result = pd.DataFrame(result)
    cursor.close()
    connection.close()
    result = result.drop_duplicates(subset=[0, 1,2,3,4,5])
    result.columns = ["PRODUCT_ID","PRODUCT_NAME","PRODUCT_LEVEL_ID","LOCATION_LEVEL_ID",
                      "LOCATION_ID","LOCATION_NAME","COMP_STR_ID","COMP_TIER","COMP_NAME","ADDR_LINE","CITY","START_DATE",
                      "SIMPLE_INDEX","BLENDED_INDEX",
                      "W_MOVEMENT_IX_REG","W_MOVEMENT_IX_PROMO",
                      "W_MARGIN_IX_REG","W_MARGIN_IX_PROMO",
                      "W_REVENUE_IX_REG","W_REVENUE_IX_PROMO",
                      "W_13WEEK_MOVEMENT_IX_REG",
                      "W_13WEEK_MOVEMENT_IX_PROMO",
                      "W_VISIT_IX_REG","W_VISIT_IX_PROMO"]
    
    if location_id is not None:
        result = result.loc[result['LOCATION_ID'] == location_id,]
            
    else:
       loc_fil = '' 
    if count_non_none == 1:
        search_list = list(set(result[comp_col]))
        closest_match = process.extractOne(name_comp, search_list)
        result = result.loc[result[comp_col] == closest_match[0],]
    if count_non_none == 2:
        search_list1 = list(set(result[comp_col]))
        search_list2 = list(set(result[comp_col1]))
        closest_match1 = process.extractOne(name_comp, search_list1)
        closest_match2 = process.extractOne(name_comp1, search_list2)
        result = result.loc[(result[comp_col] == closest_match1[0]) & (result[comp_col1] == closest_match2[0]),]
    return result


def product_level_identifier(child_prod_level):
    

    
    query = '''SELECT  * FROM PRODUCT_GROUP_TYPE'''
    connection = cx_Oracle.connect(username , password,dbname )
    cursor = connection.cursor()
    cursor.execute( query)
    result  = cursor.fetchall()
    result  = pd.DataFrame(result)
    
    cursor.close()
    connection.close()
    product_level_list = list(result.iloc[:,1])
    closest_match = process.extractOne(child_prod_level, product_level_list)
    product_level_id = result.loc[result.iloc[:,1] == closest_match[0] ,]
    return product_level_id.iloc[0,0]
def comp_parser( comp_city = None,comp_addr = None,
                     comp_name = None, comp_tier = None):
    base_loc_name = None
    count_non_none = 0
    comp_col = comp_col1 = name_comp = name_comp1 = ''
   
    if base_loc_name is not None:
        count_non_none += 1
    if comp_city is not None:
        count_non_none += 1
    if comp_addr is not None:
        count_non_none += 1
    if comp_name is not None:
        count_non_none += 1
    if comp_tier is not None:
        count_non_none += 1
    
    if count_non_none == 1: 
        if base_loc_name is not None:
            comp_col = "LOCATION_NAME"
            name_comp = base_loc_name
        if comp_city is not None:
            comp_col = "CITY"
            name_comp = comp_city
        if comp_addr is not None:
            comp_col = "ADDR_LINE1"
            name_comp = comp_addr
        if comp_tier is not None:
            comp_col = "COMP_TIER"
            name_comp = comp_tier 
        if comp_name is not None:
            comp_col = "COMP_NAME"
            name_comp = comp_name
        comp_col1 = None
        name_comp1 = None
    elif count_non_none == 2:
        if base_loc_name is not None:
            comp_col = "LOCATION_NAME"
            name_comp = base_loc_name
            if comp_city is not None:
                comp_col1 = "CITY"
                name_comp1 = comp_city
            elif comp_addr is not None:
                comp_col1 = "ADDR_LINE1"
                name_comp1 = comp_addr
            elif comp_tier is not None:
                comp_col1 = "COMP_TIER"
                name_comp1 = comp_tier 
            elif comp_name is not None:
                comp_col1 = "COMP_NAME"
                name_comp1 = comp_name
        elif comp_city  is not None:
            comp_col = "CITY"
            name_comp = comp_city
            if comp_addr is not None:
                comp_col1 = "ADDR_LINE1"
                name_comp1 = comp_addr
            elif comp_tier is not None:
                comp_col1 = "COMP_TIER"
                name_comp1 = comp_tier 
            elif comp_name is not None:
                comp_col1 = "COMP_NAME"
                name_comp1 = comp_name
        elif  comp_addr is not None:
            comp_col = "ADDR_LINE1"
            name_comp = comp_addr
            if comp_tier is not None:
                comp_col1 = "COMP_TIER"
                name_comp1 = comp_tier 
            elif comp_name is not None:
                comp_col1 = "COMP_NAME"
                name_comp1 = comp_name 
        elif comp_tier is not None:
            comp_col = "COMP_TIER"
            name_comp = comp_tier 
            if comp_name is not None:
                comp_col1 = "COMP_NAME"
                name_comp1 = comp_name 
    return count_non_none, comp_col,name_comp,comp_col1,name_comp1
    

def plotting_api(data, plot_type = 'table', metric_cols = ['sales'],
                 product_col = 'product-name', location_col = 'location-name'):
    
    df = pd.DataFrame(data)

    if 'week-no' in df.columns:
        time_col = 'week-no'
    elif 'period-no' in df.columns:
        time_col = 'period-no'
    elif 'quarter-no' in df.columns:
        time_col = 'quarter-no'
    else:
        time_col = 'cal-year'
        
    time_cols = ['cal-year', time_col] if time_col != 'cal-year' else ['cal-year']

    if isinstance(metric_cols, str):
        metric_cols = [word.strip() for word in metric_cols.split(',')]

    id_cols = time_cols + [product_col] + [location_col]
    all_cols = time_cols + [product_col] + [location_col] + metric_cols

    df = df[all_cols]
    df = df.drop_duplicates(subset=id_cols)

    unique_times = [int(x) for x in df[time_cols].drop_duplicates().loc[:, time_col].values]
    products = sorted(df[product_col].unique())
    locations = sorted(df[location_col].unique())

    if plot_type == 'line':
        options = { 'xaxis' : { time_col : unique_times}}
        
        if len(products) > 1 and  len(locations) == len(metric_cols) == 1:
            df_wide = df.pivot(index = time_cols, columns = product_col, values = metric_cols).fillna(0).round(2)
            cols = [f'{col[1]}' for col in df_wide.columns]
            df_wide.columns = cols
            
        elif len(locations) > 1 and  len(products) == len(metric_cols) == 1:
            df_wide = df.pivot(index = time_cols, columns = location_col, values = metric_cols).fillna(0).round(2)
            cols = [f'{col[1]}' for col in df_wide.columns]
            df_wide.columns = cols
            
        elif len(metric_cols) >= 1 and len(products) == len(locations) == 1:
            df_wide = df[metric_cols].fillna(0).round(2)
            cols = df_wide.columns
            
        else:
            df_wide = df.groupby(time_cols)[metric_cols].sum().fillna(0).round(2)
            cols = df_wide.columns
            
        series = [{'name': col, 'data': df_wide[col].tolist()} for col in cols]
        res = {'type': plot_type,  'options' : options, 'series' : series}
        
    elif plot_type == 'bar':
        
        if len(products) > 1:
            options = { 'xaxis' : { product_col : products}}
            df_wide = df.groupby(product_col)[metric_cols].sum().fillna(0).round(2)
            cols = df_wide.columns
            
        elif len(locations) > 1:
            options = { 'xaxis' : { location_col : locations}}
            df_wide = df.groupby(location_col)[metric_cols].sum().fillna(0).round(2)
            cols = df_wide.columns
        
        else: 
            options = { 'xaxis' : { time_col : unique_times}}
            df_wide = df[metric_cols].fillna(0).round(2)
            cols = df_wide.columns
            
        series = [{'name': col, 'data': df_wide[col].tolist()} for col in cols]
        res = {'type': plot_type,  'options' : options, 'series' : series}
        
    elif plot_type == 'table':
        df.columns = [x.replace('-', ' ').title() for x in df.columns]
        tableData1 = df.fillna(0).round(2).to_dict(orient = 'records')
        res = {'type': plot_type,  'tableData1' : tableData1}
        
    else:
        print("chart type not supoorted !!!")
        res = {'Error': 'chart type not supported!'}

    return res