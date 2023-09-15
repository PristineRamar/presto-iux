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
def cal_q():
    cal_qr = ''
    cal_qr = '''SELECT max(start_date) START_DATE, max(start_date)+6 END_DATE 
    FROM pi_selection_criteria '''
    connection = cx_Oracle.connect(username , password,dbname )
    cursor = connection.cursor()
    cursor.execute(cal_qr)
    result = cursor.fetchall()
    result = pd.DataFrame(result)
    cursor.close()
    connection.close()
    start_date = result.iloc[0,0].strftime('%Y-%m-%d')
    end_date = result.iloc[0,1].strftime('%Y-%m-%d')
    return start_date, end_date

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
             cal_type = 'W', user_id = None,cal_agg = 'N',pi_type = "S",weighted_by = None,
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
    
    quarter = process_variable (quarter)
    
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
    
    
    if  cal_type == 'Q' and quarter is None and start_date is None:
        quarter = 'Last 1'
    if  cal_type == 'W' and week is None  and start_date is None:
        week = 'Last 1'
    if  cal_type == 'P' and period is None and start_date is None:
        period = 'Last 1'  
    
           # if  cal_type is None and quarter is not None:
    #     cal_type = 'Q'
    # if  cal_type is None and week is not None:
    #     cal_type = 'W'
    # if  cal_type is None and period is not None:
    #     period = 'P'     
    
    cal_year, quarter, period, week, day, start_date, end_date, calendar_id = cal_logic(cal_year, quarter, period, week, day, start_date, end_date, calendar_id)
    if start_date is not None:
       if len(start_date) == 0:
           start_date = None
       if len(end_date) == 0:
           end_date = None
    if product_name is not None:
        if product_name in ['All','all','any']:
            product_name = None
    if  (start_date is None) and (quarter is None) and (period is None) and ( week is None) and (day is None):
        start_date, end_date = cal_q()
        cal_type = 'W'
    
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
        loc_names = [None]
   
    
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
        result, com_name_act = prod_level_query(product_id,prod_id_cat,child_prod_level, child_prod_cat_name, child_prod_id_cat,start_date,end_date, location_id,comp_city,
         comp_addr, comp_name, comp_tier , product_agg,loc_agg,cal_agg,pi_type,weighted_by)  
    #2. Get PI for all products at a child_product level under a product_level
    #PI Report  at any calendar range for a child_product level under a product_level
    if  (product_level is not None and child_prod_level is None) or  (product_level is not None and child_prod_level is not None) or (product_level is None and child_prod_level is not None):
        prod_id_cat, child_prod_cat_name, child_prod_id_cat = child_prod_query_string(child_prod_level,product_level)
        result,com_name_act = prod_level_query(product_id,prod_id_cat, child_prod_cat_name,child_prod_level, child_prod_id_cat,start_date,end_date,location_id, comp_city,
         comp_addr,comp_name,comp_tier, product_agg,loc_agg,cal_agg,pi_type,weighted_by)  
    
    # Aggregation levels

    df = result.copy()
    df = pd.DataFrame(df)
    df.set_index(df.columns[0], inplace=True)
    idx_dtype = pd.api.types.is_datetime64_any_dtype(df.index)
    if idx_dtype == True: 
        df.index = df.index.strftime('%Y-%m-%d')
    df.reset_index(inplace=True)
    json_data = df.to_json()
    if len(com_name_act) > 1:
        com_name_act = [None]
    meta_data = {
        "timeframe": start_date + " - " + end_date,
        "locations": loc_names,
        "products": [product_name],
        "competitor": com_name_act
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
    


def prod_level_query(product_id,prod_id_cat, child_prod_cat_name, child_prod_level,
                     child_prod_id_cat,start_date,end_date, location_id,  comp_city,
                      comp_addr,
                      comp_name,
                      comp_tier,product_agg,loc_agg,cal_agg,pi_type,weighted_by):
    comp_fil = ''
    loc_fil = ''
    prod_fil = ''
    loc_sp = ''
    if comp_city is not None or comp_addr is not None or comp_name is not None or comp_tier is not None:
        comp_str_id, com_name_act= comp_parser( location_id,comp_city,comp_addr,comp_name, comp_tier)
    else:
        comp_str_id, com_name_act= comp_parser( location_id,comp_city,comp_addr,comp_name, comp_tier = 'Primary')
    if len(comp_str_id) == 1:
        comp_fil = 'and PS.COMP_LOCATION_ID IN ({})'.format(comp_str_id[0])
    else:
        comp_fil = 'and PS.COMP_LOCATION_ID IN {}'.format(tuple(comp_str_id))
            
    if location_id is not None:
        loc_fil = "AND BASE_LOCATION_ID = {}".format(location_id)
    else:
        loc_fil =''
    if prod_id_cat !=None and product_id != None:
        prod_fil = "and {}={}".format(prod_id_cat,product_id)
    else:
        prod_fil = ''
    if (product_agg == 'Y') or (product_agg == 'N' and loc_agg == 'N' and cal_agg == 'N'):
        groupby_para = child_prod_cat_name
    if loc_agg == 'Y':
        groupby_para = "LOCATION_NAME"
        loc_sp =  "HAVING LOCATION_NAME IS NOT NULL"
    if cal_agg == 'Y':
        groupby_para = "START_DATE"
    if child_prod_level is None:
        child_prod_level = 4
   
   # Index mean types
    if pi_type == 'S' and weighted_by is None : 
        measure_para = "SIMPLE_INDEX"
    elif pi_type == 'B' and weighted_by is None:
        measure_para = "BLENDED_INDEX"
    elif pi_type == 'S'  and weighted_by == 'M':
        measure_para  = "W_MOVEMENT_IX_REG"
    elif pi_type == 'B'  and weighted_by == 'M':
        measure_para  = "W_MOVEMENT_IX_PROMO"
    elif pi_type == 'S'  and weighted_by == 'MR':
        measure_para  = "W_MARGIN_IX_REG"
    elif pi_type == 'B'  and weighted_by == 'MR':
        measure_para  = "W_MARGIN_IX_PROMO"
    elif pi_type == 'S'  and weighted_by == 'R':
        measure_para  = "W_REVENUE_IX_REG"
    elif pi_type == 'B'  and weighted_by == 'R':
        measure_para  = "W_REVENUE_IX_PROMO"
    elif pi_type == 'S'  and weighted_by == 'M13':
        measure_para  = "W_13WEEK_MOVEMENT_IX_REG"
    elif pi_type == 'B'  and weighted_by == 'M13':
        measure_para  = "W_13WEEK_MOVEMENT_IX_PROMO"
    elif pi_type == 'S'  and weighted_by == 'V':
        measure_para  = "W_VISIT_IX_REG"
    elif pi_type == 'B'  and weighted_by == 'V':
        measure_para  = "W_VISIT_IX_PROMO"
    else:
        measure_para  = "SIMPLE_INDEX"
    
    
    query = ''
    if child_prod_id_cat != 'ITEM_CODE': 
  
        query = '''WITH PI_TABLE AS (SELECT pid.product_id,
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
                            pid.product_id in (SELECT {child_prod_id_cat} FROM
                                               ITEM_DETAILS_VIEW WHERE ACTIVE_INDICATOR = 'Y' {prod_fil})   and 
                            ps.start_date >= to_date('{start_date}','YYYY-MM-DD')
                            and ps.start_date <= to_date('{end_date}','YYYY-MM-DD') {loc_fil} {comp_fil} ),
                PROD_DATA AS (                
                    select PRODUCT_ID {child_prod_id_cat}, NAME {child_prod_cat_name} FROM PRODUCT_GROUP WHERE ACTIVE_INDICATOR = 'Y' AND PRODUCT_LEVEL_ID = {child_prod_level}),
                 
                COMP_DATA AS (SELECT RPZ.PRICE_ZONE_ID LOCATION_ID,RPZ.ZONE_NUM LOCATION_NAME,PRIMARY_COMP_STR_ID COMP_STR_ID,'Primary' as COMP_TIER,CS.NAME COMP_NAME,CS.ADDR_LINE1,CS.CITY  FROM RETAIL_PRICE_ZONE RPZ LEFT JOIN COMPETITOR_STORE CS
                                ON 
                            RPZ.PRIMARY_COMP_STR_ID = CS.COMP_STR_ID
                            WHERE RPZ.PRIMARY_COMP_STR_ID IS NOT NULL AND RPZ.ACTIVE_INDICATOR = 'Y'
                            UNION ALL
                            SELECT RPZ.PRICE_ZONE_ID LOCATION_ID,RPZ.ZONE_NUM LOCATION_NAME,SECONDARY_COMP_STR_ID_1 COMP_STR_ID,'Secondary' as COMP_TIER,CS.NAME COMP_NAME,CS.ADDR_LINE1,CS.CITY  FROM RETAIL_PRICE_ZONE RPZ LEFT JOIN COMPETITOR_STORE CS
                                ON 
                            RPZ.SECONDARY_COMP_STR_ID_1 = CS.COMP_STR_ID
                            WHERE SECONDARY_COMP_STR_ID_1 IS NOT NULL AND  RPZ.ACTIVE_INDICATOR = 'Y' )


            SELECT   {groupby_para},round(AVG({measure_para}),2) price_index
                    FROM PI_TABLE PI LEFT JOIN PROD_DATA PD
                    ON
                    PI.PRODUCT_ID = PD.{child_prod_id_cat}
                    LEFT JOIN COMP_DATA CD
                   ON PI.COMP_STR_ID  = CD.COMP_STR_ID
                  AND PI.BASE_LOCATION_ID = CD.LOCATION_ID
                  GROUP BY  {groupby_para} {loc_sp}
                  '''.format(prod_fil = prod_fil,start_date = start_date,end_date = end_date, 
                  loc_fil = loc_fil,comp_fil = comp_fil,child_prod_id_cat=child_prod_id_cat,child_prod_level=child_prod_level,
                  child_prod_cat_name= child_prod_cat_name, measure_para = measure_para,groupby_para = groupby_para, loc_sp = loc_sp)
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
                           
                            pid.ITEM_CODE in (SELECT {child_prod_id_cat} FROM
                                               ITEM_DETAILS_VIEW WHERE ACTIVE_INDICATOR = 'Y' {prod_fil})   and 
                            ps.start_date >= to_date('{start_date}','YYYY-MM-DD')
                            and ps.start_date <= to_date('{end_date}','YYYY-MM-DD') {loc_fil} {comp_fil} ),
                PROD_DATA AS (                
                    select PRODUCT_ID {child_prod_id_cat}, NAME {child_prod_cat_name} FROM PRODUCT_GROUP WHERE ACTIVE_INDICATOR = 'Y' AND PRODUCT_LEVEL_ID = {child_prod_level}),
                 
                COMP_DATA AS (SELECT RPZ.PRICE_ZONE_ID LOCATION_ID,RPZ.ZONE_NUM LOCATION_NAME,PRIMARY_COMP_STR_ID COMP_STR_ID,'Primary' as COMP_TIER,CS.NAME COMP_NAME,CS.ADDR_LINE1,CS.CITY  FROM RETAIL_PRICE_ZONE RPZ LEFT JOIN COMPETITOR_STORE CS
                                ON 
                            RPZ.PRIMARY_COMP_STR_ID = CS.COMP_STR_ID
                            WHERE RPZ.PRIMARY_COMP_STR_ID IS NOT NULL AND RPZ.ACTIVE_INDICATOR = 'Y'
                            UNION ALL
                            SELECT RPZ.PRICE_ZONE_ID LOCATION_ID,RPZ.ZONE_NUM LOCATION_NAME,SECONDARY_COMP_STR_ID_1 COMP_STR_ID,'Secondary' as COMP_TIER,CS.NAME COMP_NAME,CS.ADDR_LINE1,CS.CITY  FROM RETAIL_PRICE_ZONE RPZ LEFT JOIN COMPETITOR_STORE CS
                                ON 
                            RPZ.SECONDARY_COMP_STR_ID_1 = CS.COMP_STR_ID
                            WHERE SECONDARY_COMP_STR_ID_1 IS NOT NULL AND  RPZ.ACTIVE_INDICATOR = 'Y' )


            SELECT   {groupby_para},round(AVG({measure_para}),2) price_index
                    FROM PI_TABLE PI LEFT JOIN PROD_DATA PD
                    ON
                    PI.PRODUCT_ID = PD.{child_prod_id_cat}
                    LEFT JOIN COMP_DATA CD
                   ON PI.COMP_STR_ID  = CD.COMP_STR_ID
                  AND PI.BASE_LOCATION_ID = CD.LOCATION_ID
                  GROUP BY  {groupby_para} {loc_sp}
                  '''.format(prod_fil = prod_fil,start_date = start_date,end_date = end_date, 
                  loc_fil = loc_fil,comp_fil = comp_fil,child_prod_id_cat=child_prod_id_cat,child_prod_level=child_prod_level,
                  child_prod_cat_name= child_prod_cat_name, measure_para = measure_para,groupby_para = groupby_para, loc_sp = loc_sp)
  
    print(query)
    connection = cx_Oracle.connect(username , password,dbname )
    cursor = connection.cursor()
    cursor.execute( query)
    result = cursor.fetchall()
    result = pd.DataFrame(result)
    cursor.close()
    connection.close()
    result = result.drop_duplicates(subset=[0, 1])
    result.columns = [groupby_para, measure_para]
    return result,com_name_act


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
def comp_parser( location_id,comp_city = None,comp_addr = None,
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
    if count_non_none == 3:
        comp_tier = None
        count_non_none = 2
    
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
    comp_query = ''
    comp_query = '''SELECT RPZ.PRICE_ZONE_ID LOCATION_ID,RPZ.ZONE_NUM LOCATION_NAME,PRIMARY_COMP_STR_ID COMP_STR_ID,'Primary' as COMP_TIER,CS.NAME COMP_NAME,CS.ADDR_LINE1,CS.CITY  FROM RETAIL_PRICE_ZONE RPZ LEFT JOIN COMPETITOR_STORE CS
                                ON 
                            RPZ.PRIMARY_COMP_STR_ID = CS.COMP_STR_ID
                            WHERE RPZ.PRIMARY_COMP_STR_ID IS NOT NULL AND RPZ.ACTIVE_INDICATOR = 'Y'
                            UNION ALL
                            SELECT RPZ.PRICE_ZONE_ID LOCATION_ID,RPZ.ZONE_NUM LOCATION_NAME,SECONDARY_COMP_STR_ID_1 COMP_STR_ID,'Secondary' as COMP_TIER,CS.NAME COMP_NAME,CS.ADDR_LINE1,CS.CITY  FROM RETAIL_PRICE_ZONE RPZ LEFT JOIN COMPETITOR_STORE CS
                                ON 
                            RPZ.SECONDARY_COMP_STR_ID_1 = CS.COMP_STR_ID
                            WHERE SECONDARY_COMP_STR_ID_1 IS NOT NULL AND  RPZ.ACTIVE_INDICATOR = 'Y' '''
    connection = cx_Oracle.connect(username , password,dbname )
    cursor = connection.cursor()
    cursor.execute(comp_query)
    result  = cursor.fetchall()
    result  = pd.DataFrame(result)
    result.columns = ["LOCATION_ID","LOCATION_NAME","COMP_STR_ID","COMP_TIER","COMP_NAME","ADDR_LINE1","CITY"]
    cursor.close()
    connection.close()
    if location_id is not None: 
        result = result.loc[result["LOCATION_ID"] == location_id,]

    if count_non_none == 1:
        key_list = []
        search_list = list(set(result[comp_col]))
        search_list = list(map(lambda x: x.lower(), search_list))
        name_comp = name_comp.lower()
        key_list = [s for s in search_list if name_comp in s]
        result[comp_col] = result[comp_col].str.lower()
        result = result.loc[result[comp_col].isin(key_list) ,]
    if count_non_none == 2:
        key_list = []
        key_list1 = []
        search_list = list(set(result[comp_col]))
        search_list = list(map(lambda x: x.lower(), search_list))
        name_comp = name_comp.lower()
        key_list = [s for s in search_list if name_comp in s]
    
        search_list1 = list(set(result[comp_col1]))
        search_list1 = list(map(lambda x: x.lower(), search_list1))
        name_comp1 = name_comp1.lower()
        key_list1 = [s for s in search_list1 if name_comp1 in s]
        result[comp_col] = result[comp_col].str.lower()
        result[comp_col1] = result[comp_col1].str.lower()
        result = result.loc[(result[comp_col].isin(key_list)) & (result[comp_col1].isin(key_list1)),]
    
    comp_str_id = list(result["COMP_STR_ID"].unique())
    com_name_act = list(result["COMP_NAME"].unique())
    return  comp_str_id, com_name_act
    

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