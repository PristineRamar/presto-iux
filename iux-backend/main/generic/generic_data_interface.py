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
from generic.generic_data_functions_common import (cal_lookup, sanitize_cal_input,
                                   parse_prod_request, parse_loc_request,
                                   prod_hier, loc_hier, product_data)
from generic.generic_data_config import (data_url, username, password, dbname, n_responses, synonyms)

# =============================================================================
# 
# =============================================================================

# Helper function for calling presto-data-services apis 

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

# Default calendar behavior if LLM fails to specify. 

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

# Sometimes LLM gives empty list, e.g. [] or list with something strange like ['all']. This catches and fixes its mistakes.
def catch_empty_list(l):
    if type(l) == list:
        l_2 = [x for x in l if x.lower() not in ['all', 'each', 'every']]
        if len(l_2) > 0:
            return l_2
        else:
            return None
    else:
        return l

# =============================================================================
# 
# =============================================================================

# Not currently used.
def sanitize_list(x):
    if type(x) == list and len(x) > 0:
        return x[0] if x[0].lower() not in ['all', 'every', 'each'] else None
    return x  

# =============================================================================
# 
# =============================================================================    

# Fetches cost data. First it, parses timeframe, product, and location. 
# Then it calls the cost api from presto-data-services. Finally, it formats
# the result. 

def cost_api(product_name = None, product_id = None, product_level = None, item_list = None,
             active = 'Y', group_name = None,
             location_name = None, location_id = None, location_level = None,
             cal_year = None, quarter = None, period = None, week = None, day = None,
             start_date = None, end_date = None, calendar_id = None, cal_type = 'W', user_id = None, change = 'All'):
    
    cal_year, quarter, period, week, day, start_date, end_date, calendar_id = cal_logic(cal_year, quarter, period, week, day, start_date, end_date, calendar_id)
       
    cal = cal_lookup(cal_year, quarter, period, week, day,
                     start_date, end_date, calendar_id, cal_type)

    if cal.empty:
        raise ValueError('timeframe')
        
    last_week = cal_lookup(week = 'last 1')
    start_week = min(cal['start-date'].min(), last_week['start-date'].min())

    location_name = catch_empty_list(location_name)    
    
    locations = parse_loc_request(location_name, location_id, location_level, active) 

    if locations.empty:
        raise ValueError('location')
               
    loc_names = list(locations['location-name'].drop_duplicates())
    locs = {l:[int(x) for x in locations.loc[locations['location-level'] == l, 'location-id']] for l in locations['location-level'].unique()}
    
    product_name = catch_empty_list(product_name)
    
    products = parse_prod_request(product_name, product_id, product_level,
                               user_id, active, n_responses) 
    
    if products.empty:
        raise ValueError('product')
        
    if (products['authorized'] == False).all():
        raise ValueError('authorization')
        
    products = products.loc[products['authorized']]
        
    prod_names = list(products['product-name'].drop_duplicates())
    prods = {p:[int(x) for x in products.loc[products['product-level'] == p, 'product-id']] for p in products['product-level'].unique()}
    
    try:
        response = call_api('/cost/get-cost-data', locs, prods, cal, active, start_week)
    except:
        raise ValueError('missing_data')
    
    response = response.rename(columns = {'calendarId':'calendar-id',
                                          'startDate':'effective-date',
                                          'locationId':'location-id',
                                          'locationLevelId':'location-level'})
    response['location-level'] = np.where(response['location-level'] == 2, 5, response['location-level'])
    response['location-level'] = np.where(response['location-level'] == 1, 6, response['location-level'])
    response['location-level'] = np.where(response['location-level'] == 0, 1, response['location-level'])
    response = response.merge(locations, how = 'left')
    
    items = response.loc[:, ['item-name', 'item-code']].drop_duplicates()
    items['key'] = 0
    extended_cal = pd.concat([cal, last_week] if last_week['start-date'].min() <= cal['end-date'].max() else [cal],
                             ignore_index = True).drop_duplicates()
    extended_cal['key'] = 0
    extended_cal = extended_cal.merge(items, on = 'key')
    extended_cal = extended_cal.merge(response, how = 'left', on = ['calendar-id', 'item-code', 'item-name'])
    extended_cal = extended_cal.sort_values(by = ['calendar-id', 'item-code'])
    extended_cal['cost'] = extended_cal.groupby(['item-code'])['cost'].transform(lambda x: x.fillna(method = 'ffill'))
    extended_cal['effective-date'] = extended_cal.groupby(['item-code'])['effective-date'].transform(lambda x: x.fillna(method = 'ffill'))

    extended_cal = extended_cal.loc[extended_cal['calendar-id'].isin(cal['calendar-id']),
                                    ['cal-year', 'quarter-no', 'period-no', 'week-no', 
                                     'start-date', 'end-date', 'location-name',
                                     'item-name', 'item-code', 'cost', 'effective-date']]
    
    extended_cal['start-date'] = extended_cal['start-date'].dt.strftime('%m/%d/%Y')
    extended_cal['end-date'] = extended_cal['end-date'].dt.strftime('%m/%d/%Y')
    extended_cal = extended_cal.rename(columns = {'start-date':'week-start-date',
                                                  'end-date':'week-end-date',
                                                  'cost':'list-cost'})
    extended_cal = extended_cal.dropna()
    
    if change == 'Yes':
        extended_cal = extended_cal.groupby(['item-name', 'item-code']).filter(lambda x: (x['list-cost'].round(2) != x['list-cost'].round(2).min()).any())
    if change == 'No':
        extended_cal = extended_cal.groupby(['item-name', 'item-code']).filter(lambda x: (x['list-cost'].round(2) == x['list-cost'].round(2).min()).all())
        
    return extended_cal, prod_names, loc_names, cal['start-date'].min().strftime('%m/%d/%Y') + ' - ' + cal['end-date'].max().strftime('%m/%d/%Y')

# =============================================================================
# 
# =============================================================================

# Same as above but with price instead of cost.

def price_api(product_name = None, product_id = None, product_level = None, item_list = None,
              active = 'Y', group_name = None,
             location_name = None, location_id = None, location_level = None,
             cal_year = None, quarter = None, period = None, week = None, day = None,
             start_date = None, end_date = None, calendar_id = None, cal_type = 'W', user_id = None, change = 'All'):
    
    cal_year, quarter, period, week, day, start_date, end_date, calendar_id = cal_logic(cal_year, quarter, period, week, day, start_date, end_date, calendar_id)
       
    cal = cal_lookup(cal_year, quarter, period, week, day,
                     start_date, end_date, calendar_id, cal_type)
    
    if cal.empty:
        raise ValueError('timeframe')
        
    last_week = cal_lookup(week = 'last 1')
    start_week = min(cal['start-date'].min(), last_week['start-date'].min())

    location_name = catch_empty_list(location_name)    
    
    locations = parse_loc_request(location_name, location_id, location_level, active) 

    if locations.empty:
        raise ValueError('location')
               
    loc_names = list(locations['location-name'].drop_duplicates())
    locs = {l:[int(x) for x in locations.loc[locations['location-level'] == l, 'location-id']] for l in locations['location-level'].unique()}
    
    product_name = catch_empty_list(product_name)
    
    products = parse_prod_request(product_name, product_id, product_level,
                               user_id, active, n_responses)

    if products.empty:
        raise ValueError('product')
        
    if (products['authorized'] == False).all():
        raise ValueError('authorization')
        
    products = products.loc[products['authorized']]
        
    prod_names = list(products['product-name'].drop_duplicates())
    prods = {p:[int(x) for x in products.loc[products['product-level'] == p, 'product-id']] for p in products['product-level'].unique()}
    
    try:
        response = call_api('/price/get-price-data', locs, prods, cal, active, start_week)
    except:
        raise ValueError('missing_data')
    
    response = response.rename(columns = {'calendarId':'calendar-id',
                                          'startDate':'effective-date',
                                          'locationId':'location-id',
                                          'locationLevelId':'location-level'})
    response['location-level'] = np.where(response['location-level'] == 2, 5, response['location-level'])
    response['location-level'] = np.where(response['location-level'] == 1, 6, response['location-level'])
    response['location-level'] = np.where(response['location-level'] == 0, 1, response['location-level'])
    response = response.merge(locations, how = 'left')
    
    items = response.loc[:, ['item-name', 'item-code']].drop_duplicates()
    items['key'] = 0
    extended_cal = pd.concat([cal, last_week] if last_week['start-date'].min() <= cal['end-date'].max() else [cal],
                             ignore_index = True).drop_duplicates()
    extended_cal['key'] = 0
    extended_cal = extended_cal.merge(items, on = 'key')
    extended_cal = extended_cal.merge(response, how = 'left', on = ['calendar-id', 'item-code', 'item-name'])
    extended_cal = extended_cal.sort_values(by = ['calendar-id', 'item-code'])
    
    extended_cal['price'] = extended_cal.groupby(['item-code'])['price'].transform(lambda x: x.fillna(method = 'ffill'))
    extended_cal['priceQty'] = extended_cal.groupby(['item-code'])['priceQty'].transform(lambda x: x.fillna(method = 'ffill'))
    extended_cal['effective-date'] = extended_cal.groupby(['item-code'])['effective-date'].transform(lambda x: x.fillna(method = 'ffill'))
    
    extended_cal = extended_cal.loc[extended_cal['calendar-id'].isin(cal['calendar-id']),
                                    ['cal-year', 'quarter-no', 'period-no', 'week-no', 
                                     'start-date', 'end-date', 'location-name',
                                     'item-name', 'item-code', 
                                     'price', 'priceQty', 'effective-date']]
    
    extended_cal['start-date'] = extended_cal['start-date'].dt.strftime('%m/%d/%Y')
    extended_cal['end-date'] = extended_cal['end-date'].dt.strftime('%m/%d/%Y')
    extended_cal = extended_cal.rename(columns = {'start-date':'week-start-date',
                                                  'end-date':'week-end-date',
                                                  'priceQty':'reg-qty',
                                                  'price':'reg-price'})
    extended_cal = extended_cal.dropna()
    
    if change == 'Yes':
        extended_cal = extended_cal.groupby(['item-name', 'item-code']).filter(lambda x: (x['reg-price'].round(2) != x['reg-price'].round(2).min()).any())
    if change == 'No':
        extended_cal = extended_cal.groupby(['item-name', 'item-code']).filter(lambda x: (x['reg-price'].round(2) == x['reg-price'].round(2).min()).all())
        
    return extended_cal, prod_names, loc_names, cal['start-date'].min().strftime('%m/%d/%Y') + ' - ' + cal['end-date'].max().strftime('%m/%d/%Y')

# =============================================================================
# 
# =============================================================================

# Same as above but with promotions instead of price.

def promotion_api(product_name = None, product_id = None, product_level = None, item_list = None,
                  active = 'Y', group_name = None,
             location_name = None, location_id = None, location_level = None,
             cal_year = None, quarter = None, period = None, week = None, day = None,
             start_date = None, end_date = None, calendar_id = None, cal_type = 'W',
             promo_type = None, page_no = None, block_no = None, user_id = None):
    
    cal_year, quarter, period, week, day, start_date, end_date, calendar_id = cal_logic(cal_year, quarter, period, week, day, start_date, end_date, calendar_id)
       
    cal = cal_lookup(cal_year, quarter, period, week, day,
                     start_date, end_date, calendar_id, cal_type) 
    
    if cal.empty:
        raise ValueError('timeframe')

    location_name = catch_empty_list(location_name)    
    
    locations = parse_loc_request(location_name, location_id, location_level, active)   

    if locations.empty:
        raise ValueError('location')
             
    loc_names = list(locations['location-name'].drop_duplicates())
    locs = {l:[int(x) for x in locations.loc[locations['location-level'] == l, 'location-id']] for l in locations['location-level'].unique()}
    
    product_name = catch_empty_list(product_name)
    
    products = parse_prod_request(product_name, product_id, product_level,
                               user_id, active, n_responses) 
    
    if products.empty:
        raise ValueError('product')
        
    if (products['authorized'] == False).all():
        raise ValueError('authorization')
        
    products = products.loc[products['authorized']]
        
    prod_names = list(products['product-name'].drop_duplicates())
    prods = {p:[int(x) for x in products.loc[products['product-level'] == p, 'product-id']] for p in products['product-level'].unique()}
    
    try:
        response = call_api('/promotion/get-promotion-data', locs, prods, cal, active)
    except:
        raise ValueError('missing_data')
    
    response = response.rename(columns = {'calendarId':'calendar-id'})
    response = response.loc[response['invalid_data'] != 'Y']    
    response['sale-price'] = np.where(response['promotionTypeId'] == 3, response['mustBuyPrice'], response['offerPrice'])
    response['sale-qty'] = np.where(response['promotionTypeId'] == 3, response['mustBuyPriceQty'], response['offerPriceQty'])
    response = response.loc[response['calendar-id'].isin(cal['calendar-id'])]
    
    response = response.rename(columns = {'startDate':'promo-start-date',
                                          'endDate':'promo-end-date',
                                          'calendarStartDate':'week-start-date',
                                          'promotionTypeName':'promo-type',
                                          'pageNumber':'page-no',
                                          'blockNumber':'block-no',
                                          'regPrice':'reg-price',
                                          'regPriceQty':'reg-qty'})
    
    response = response.loc[:, ['week-start-date', 'item-name', 'promo-type',
                                'reg-price', 'reg-qty', 'sale-price', 'sale-qty',
                                'promo-start-date', 'promo-end-date', 
                                'page-no', 'block-no']].drop_duplicates()
    
    response['block-no'] = response['block-no'].replace(0, np.nan)
    response['page-no'] = response['page-no'].replace(0, np.nan)
    response = response.sort_values(by = ['item-name', 'promo-start-date', 'promo-type',
                                          'sale-price', 'sale-qty', 'page-no', 'block-no'])
    response = response.groupby(['item-name', 'week-start-date', 'promo-type',
                                 'sale-price', 'sale-qty', 'promo-start-date',
                                 'promo-end-date']).first().reset_index()
    response = response.sort_values(by = ['item-name', 'promo-start-date', 'promo-type',
                                          'sale-price', 'sale-qty', 'page-no', 'block-no'])
    
    prices = price_api(product_name = product_name, product_id = product_id, product_level = product_level,
                       item_list = item_list, active = active,
                       location_name = location_name, location_id = location_id, location_level = location_level,
                       cal_year = cal_year, quarter = quarter, period = period, week = week, day = day,
                       start_date = start_date, end_date = end_date, calendar_id = calendar_id, cal_type = cal_type,
                       user_id = user_id, change = 'A')[0]
    
    response = response.merge(prices.loc[:, ['week-start-date', 'item-name', 'reg-price', 'reg-qty']],
                              how = 'inner')
    
    response = response.loc[:, ['item-name', 'reg-price', 'reg-qty', 'sale-price', 'sale-qty',
                                'promo-type', 'promo-start-date', 'promo-end-date', 'page-no', 'block-no']]
    response = response.drop_duplicates()
    
    if promo_type is not None:
        if type(promo_type) == str:
            response = response.loc[response['promo-type'] == promo_type]
        if type(promo_type) == list:
            response = response.loc[response['promo-type'].isin(promo_type)]
            
    if page_no is not None:
        if type(page_no) in [int, float]:
            response = response.loc[response['page-no'] == page_no]
        if type(page_no) == list:
            response = response.loc[response['page-no'].isin([int(x) for x in page_no if type(x) in [int, float]])]
            
    if block_no is not None:
        if type(block_no) in [int, float]:
            response = response.loc[response['block-no'] == block_no]
        if type(block_no) == list:
            response = response.loc[response['block-no'].isin([int(x) for x in block_no if type(x) in [int, float]])]        
                       
    return response, prod_names, loc_names, cal['start-date'].min().strftime('%m/%d/%Y') + ' - ' + cal['end-date'].max().strftime('%m/%d/%Y')

# =============================================================================
# 
# =============================================================================

# Similar to above but with movement/sales/margin. Major difference is it queries sales analysis instead of
# using presto-data-services.

def movement_api(product_name = None, product_id = None, product_level = None, item_list = None,
                 active = 'Y', group_name = None, 
                 location_name = None, location_id = None, location_level = None,
                 product_detail_level = None, location_detail_level = None,
                 cal_year = None, quarter = None, period = None, week = None, day = None,
                 start_date = None, end_date = None, calendar_id = None, cal_type = 'W',
                 promoted = 'All', user_id = None):    
    
    # group name specifices at what level the user wants data to be aggregated.
    # E.g. if they want Grocery sales at the category/period level, then group_name = ['Catgeory', 'Period']
    # will do the trick. Uses the list of synonyms to figure out what to do.
    if group_name:
        syns = synonyms.copy(deep = True)
        syns['match'] = False
        if type(group_name) == str:
            group_name = [group_name]
        for g in group_name:
            match = extractOne(g,
                               list(synonyms['name'].values),
                               scorer = QRatio,
                               score_cutoff = 75)
            if match:
                syns.loc[syns['name'] == match[0], 'match'] = True
       
        for i, row in syns.loc[syns['match']].iterrows():
            if row['type'] == 'cal':
                cal_type = row['name'][0]
            if row['type'] == 'prod':
                product_detail_level = int(row['level'])
                product_col_name = row['name']
            if row['type'] == 'loc':
                location_detail_level = int(row['level'])
                location_col_name = row['name']
        
    cal_year, quarter, period, week, day, start_date, end_date, calendar_id = cal_logic(cal_year, quarter, period, week, day, start_date, end_date, calendar_id)
     
    cal = cal_lookup(cal_year, quarter, period, week, day,
                     start_date, end_date, calendar_id, cal_type)

    if cal.empty:
        raise ValueError('timeframe')
    
    location_name = catch_empty_list(location_name) 
    
    locations = parse_loc_request(location_name, location_id, location_level, active)

    if locations.empty:
        raise ValueError('location')
        
    if location_detail_level:
        temp = loc_hier(location_id = [int(x) for x in locations['location-id'].values],
                        location_level = locations['location-level'].max(),
                        detail_level = location_detail_level)
        col_match = extractOne(location_col_name, list(temp.columns))
        if col_match:
            col_match = col_match[0]
        locations = parse_loc_request(location_id = list(temp[col_match].values),
                                      location_level = location_detail_level,
                                      active = active)
              
    loc_names = list(locations['location-name'].drop_duplicates())
    locs = {l:[int(x) for x in locations.loc[locations['location-level'] == l, 'location-id']] for l in locations['location-level'].unique()}
    
    product_name = catch_empty_list(product_name)
    
    products = parse_prod_request(product_name, product_id, product_level,
                                  user_id, active, n_responses)
    
    if products.empty:
        raise ValueError('product')
        
    if (products['authorized'] == False).all():
        raise ValueError('authorization')
        
    products = products.loc[products['authorized']]
    
    if product_detail_level:
        temp = prod_hier(product_id = [int(x) for x in products['product-id'].values],
                         product_level = products['product-level'].max(),
                         detail_level = product_detail_level)        
        col_match = extractOne(product_col_name, list(temp.select_dtypes(include=[np.number]).columns.values))
        if col_match:
            col_match = col_match[0]
        products = parse_prod_request(product_id = list(temp[col_match].values),
                                      product_level = product_detail_level,
                                      active = active)
    
    prod_names = list(products['product-name'].drop_duplicates())
    prods = {p:[int(x) for x in products.loc[products['product-level'] == p, 'product-id']] for p in products['product-level'].unique()}
    
    if len(products) >= 10 ** 3 or len(locations) >= 10 ** 3 or len(cal) >= 10 ** 3:
        raise ValueError('data_size')
        
    responses = []
    base_table_name = 'sales_aggr' + ('_daily' if cal_type == 'D' else '_weekly' if cal_type == 'W' else '')
    for l in locs:
        table_name = base_table_name + '_rollup' if l <= 4 else base_table_name
        for p in prods:
            if l != 6:
                query = """
                select
                    calendar_id,
                    location_id,
                    location_level_id,
                    product_id,
                    product_level_id,
                    tot_visit_cnt,
                    tot_movement,
                    reg_movement,
                    sale_movement,
                    tot_revenue,
                    reg_revenue,
                    sale_revenue,
                    tot_margin,
                    reg_margin,
                    sale_margin,
                    avg_order_size
                from {table_name}
                where calendar_id in ({calendar_list})
                and location_level_id = {location_level}
                and location_id in ({location_list})
                """.format(table_name = table_name,
                           location_level = l,
                           location_list = ', '.join([str(x) for x in locs[l]]),
                           calendar_list = ', '.join(str(x) for x in cal['calendar-id'].values))
    
                if p != 99:
                    query += """
                    and product_level_id = {product_level}
                    and product_id in ({product_list})
                    """.format(product_level = p,
                               product_list = ', '.join([str(x) for x in prods[p]]))
                else:
                    query += """
                    and product_level_id is null
                    and product_id is null
                    """
                    
            else:
                query = """
                select 
                    calendar_id,
                    price_zone_id location_id,
                    6 as location_level_id,
                    product_id,
                    product_level_id,
                    sum(tot_visit_cnt) tot_visit_cnt,
                    sum(tot_movement) tot_movement,
                    sum(reg_movement) reg_movement,
                    sum(sale_movement) sale_movement,
                    sum(tot_revenue) tot_revenue,
                    sum(reg_revenue) reg_revenue,
                    sum(sale_revenue) sale_revenue,
                    sum(tot_margin) tot_margin,
                    sum(reg_margin) reg_margin,
                    sum(sale_margin) sale_margin,
                    avg(avg_order_size) avg_order_size
                from {table_name} sa
                join (select comp_str_id, price_zone_id from competitor_store
                      where price_zone_id in ({location_list})) cs
                    on cs.comp_str_id = sa.location_id
                    and sa.location_level_id = 5
                where calendar_id in ({calendar_list})
                """.format(table_name = table_name,
                           location_list = ', '.join([str(x) for x in locs[l]]),
                           calendar_list = ', '.join(str(x) for x in cal['calendar-id'].values)) 
        
                if p != 99:
                    query += """
                    and product_level_id = {product_level}
                    and product_id in ({product_list})
                    """.format(product_level = p,
                               product_list = ', '.join([str(x) for x in prods[p]]))
                else:
                    query += """
                    and product_level_id is null
                    and product_id is null
                    """
                    
                query += """
                group by
                    calendar_id,
                    price_zone_id,
                    product_id,
                    product_level_id
                """
                
            connection = cx_Oracle.connect(username, password, dbname)
            f = open("demofile2.txt", "a")
            f.write(query)
            f.close()
            response = pd.read_sql(query, connection)
            connection.close()
            response.columns = [x.lower().replace('_', '-') for x in response.columns]
            if response.empty:
                continue
            responses.append(response)
    
    try:
        response = pd.concat(responses, ignore_index = True)
    except:
        raise ValueError('missing_data')
    
    response = response.rename(columns = {'location-level-id':'location-level',
                                          'product-level-id':'product-level',
                                          'tot-visit-cnt': 'visits'})
    if 99 in products['product-level'].values:
        response['product-id'] = response['product-id'].fillna(products.loc[products['product-level'] == 99, 'product-id'].iloc[0])
        response['product-level'] = response['product-level'].fillna(99)
    
    if promoted == 'Yes':
        response['movement'] = response['sale-movement']
        response['sales'] = response['sale-revenue']
        response['margin'] = response['sale-margin']
    elif promoted == 'No':
        response['movement'] = response['reg-movement']
        response['sales'] = response['reg-revenue']
        response['margin'] = response['reg-margin']
    else:
        response['movement'] = response['tot-movement']
        response['sales'] = response['tot-revenue']
        response['margin'] = response['tot-margin']
        
    response = response.merge(cal, how = 'left', on = 'calendar-id')
    response = response.merge(products, how = 'left', on = ['product-id', 'product-level']) 
    response = response.merge(locations, how = 'left', on = ['location-id', 'location-level']) 
    
    if (response['margin'] == 0).all():
        rate = np.random.normal(loc = 0.3, scale = 0.05, size = len(response))
        response['margin'] = (rate * response['sales']).round(2)
        
    response = response.loc[:, [x for x in ['cal-year', 'quarter-no', 'period-no', 'week-no', 'day-no',
                                'start-date', 'end-date'] if x in cal.columns] + ['location-name', 'product-name', 
                                'movement', 'sales', 'margin', 'visits', 'avg-order-size']]
    response = response.sort_values([x for x in ['cal-year', 'quarter-no', 'period-no', 'week-no', 'day-no',
                                'start-date', 'end-date'] if x in cal.columns] + ['location-name', 'product-name'])
    response['end-date'] = response['end-date'].fillna(response['start-date']).dt.strftime('%m/%d/%Y')
    response['start-date'] = response['start-date'].dt.strftime('%m/%d/%Y')
    
    if n_responses > 1:
        response = response.groupby([x for x in ['cal-year', 'quarter-no', 'period-no', 'week-no', 'day-no',
                                    'start-date', 'end-date'] if x in cal.columns] + ['location-name', 'product-name'])
        response = response.agg({'movement':'sum', 'sales':'sum', 'margin':'sum',
                                 'visits':'sum', 'avg-order-size':'mean'}).reset_index()
    
    response['margin-rate'] = (response['margin'] / response['sales']).fillna(0)
    response['avg-selling-price'] = (response['sales'] / response['movement']).fillna(0)
    return response, prod_names, loc_names, cal['start-date'].min().strftime('%m/%d/%Y') + ' - ' + cal['end-date'].fillna(cal['start-date']).max().strftime('%m/%d/%Y')

# =============================================================================
# 
# =============================================================================

# Originally, we thought we might have the LLM look up the product hierarchy itself, but we never got to it.
# Not currently in use.
def hier_api(product_name = None, product_id = None, product_level = None, detail_level = None,
             other_levels = [5, 4, 3, 2, 1.5, 1], active = 'Y'):
    
    return prod_hier(product_name = product_name, product_id = product_id, product_level = product_level,
                     detail_level = detail_level, other_levels = other_levels, active = active)

# =============================================================================
# 
# =============================================================================

# LLM will call this when it wants to format the data for plotting a table or chart.

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
        raise ValueError('chart_type')

    return res