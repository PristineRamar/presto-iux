# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 13:26:14 2023

@author: Dan
"""

import pandas as pd
import numpy as np
import re
import cx_Oracle
import json

from datetime import datetime
from rapidfuzz.process import extractOne
from rapidfuzz.fuzz import QRatio
from generic.generic_data_config import (username, dbname, password, all_prod_id,
                   global_zone_id, chain_id, queries, product_data, location_data, cal_data, synonyms)

# =============================================================================
# 
# =============================================================================


# This is a helper function which sanitizes calendar lookup input. The LLM had a habit of 
# using things like week = ['W3', 'W4'] instead of just week = [3, 4]. This catches its 
# common mistakes.

def sanitize_cal_input(cal_year = None, quarter = None, period = None, week = None, day = None):
    
    if type(cal_year) == list:
        if len(cal_year) == 1:
            cal_year = cal_year[0]
        else:
            for j, c in enumerate(cal_year):
                cal_year[j] = sanitize_cal_input(cal_year = cal_year[j])[0]                
    if type(quarter) == list:
        if len(quarter) == 1:
            quarter = quarter[0]
        else:
            for j, c in enumerate(quarter):
                quarter[j] = sanitize_cal_input(quarter = quarter[j])[1]    
    if type(period) == list:
        if len(period) == 1:
            period = period[0]
        else:
            for j, c in enumerate(period):
                period[j] = sanitize_cal_input(period = period[j])[2]                
    if type(week) == list:
        if len(week) == 1:
            week = week[0]
        else:
            for j, c in enumerate(week):
                week[j] = sanitize_cal_input(week = week[j])[3]                
    if type(day) == list:
        if len(day) == 1:
            day = day[0]
        else:
            for j, c in enumerate(day):
                day[j] = sanitize_cal_input(day = day[j])[4]
    
    if type(cal_year) == str:
        cal_year = cal_year.lower()
        cal_year = cal_year + ' 1' if cal_year in ['next', 'last'] else cal_year
        cal_year = int(cal_year) if cal_year.isnumeric() else cal_year
    if type(quarter) == str:
        quarter = quarter.lower()
        quarter = quarter + ' 1' if quarter in ['next', 'last'] else quarter
        quarter = int(quarter) if quarter.isnumeric() else int(re.sub('q', '', quarter)) if bool(re.match('^q[0-9]+$', quarter)) else quarter   
    if type(period) == str:
        period = period.lower()
        period = period + ' 1' if period in ['next', 'last'] else period
        period = int(period) if period.isnumeric() else int(re.sub('p', '', period)) if bool(re.match('^p[0-9]+$', period)) else period  
    if type(week) == str:
        week = week.lower()
        week = week + ' 1' if week in ['next', 'last'] else week
        week = int(week) if week.isnumeric() else int(re.sub('w', '', week)) if bool(re.match('^w[0-9]+$', week)) else week
    if type(day) == str:
        day = day.lower()
        day = day + ' 1' if day in ['next', 'last'] else day
        day = int(day) if day.isnumeric() else int(re.sub('d', '', day)) if bool(re.match('^d[0-9]+$', day)) else day
        
    return cal_year, quarter, period, week, day

# =============================================================================
# 
# =============================================================================


# For searching through the calendar. Inputs are as follows:
# cal_type -- 'Y', 'Q', 'P', 'W', or 'D'
# calendar_id -- For searching for a specific calendar id or list of such, e.g. 1234 or [1234, 5678]
# start_date, end_date -- For searching between given dates. Can be strings recognizable as datetime, e.g. '2022-01-17'.
# cal_year -- For filtering results by specific calendar year or list of such, e.g. 2023 or [2022, 2023]. Can also use a few key phrases like 'current', 'next 4', or 'last 2'
# quarter -- For filtering results by specific quarter or list of such, e.g. 4 or [1, 2]. Can also use a few key phrases like 'current', 'next 4', or 'last 2'.
# period -- Same as above but with period instead of quarter. This is done relative to any year/quarter filtering already done. So, e.g., quarter = 3, period = 2 will give the second period of Q3
# week -- Same as above but with week instead of period.
# day -- Same as above but with day instead of week.

def cal_lookup(cal_year = None, quarter = None, period = None, week = None, day = None, 
               start_date = None, end_date = None, calendar_id = None, cal_type = 'W'):
    
    cal_year, quarter, period, week, day = sanitize_cal_input(cal_year, quarter, period, week, day)
    
    if cal_type in cal_data:
        response = cal_data[cal_type].copy(deep = True)
    
    else:
        if cal_type not in ['D', 'W', 'P', 'Q', 'Y']:
            cal_type = 'W'
            
        cols = """
        cal_year,"""
        
        if cal_type in ['Q', 'P', 'W', 'D']:
            cols += """
            quarter_no,"""
        
        if cal_type in ['P', 'W', 'D']:
            cols += """
            period_no,"""
            
        if cal_type in ['W', 'D']:
            cols += """
            week_no,"""
            
        if cal_type == 'D':
            cols += """
            day_no,
            """
        
        cols += """
        d.start_date,
        d.end_date,
        d.calendar_id
        """   
    
        cal_query = """
          select distinct
              {}
          from 
          (select
             cal_year, 
             start_date,
             end_date,
             calendar_id,
             actual_no day_no,
             row_type
           from retail_calendar
           order by start_date) d
            left join 
              (select
                 actual_no week_no,
                 start_date week_start_date,
                 end_date week_end_date
               from retail_calendar
               where row_type = 'W') w
            on d.start_date between w.week_start_date and w.week_end_date
            left join 
              (select 
                 actual_no period_no, 
                 start_date period_start_date, 
                 end_date period_end_date 
               from retail_calendar 
               where row_type = 'P') p
            on d.start_date between p.period_start_date and p.period_end_date
            left join 
              (select 
                 actual_no quarter_no, 
                 start_date quarter_start_date, 
                 end_date quarter_end_date 
               from retail_calendar 
               where row_type = 'Q') q
            on d.start_date between q.quarter_start_date and q.quarter_end_date
            left join 
              (select
                 start_date year_start_date, 
                 end_date year_end_date 
               from retail_calendar 
               where row_type = 'Y') y
            on d.start_date between y.year_start_date and y.year_end_date
            where d.row_type = '{}'
            and cal_year >= 2013
            order by d.start_date
            """.format(cols, cal_type)
        
        connection = cx_Oracle.connect(username, password, dbname)
        response = pd.read_sql(cal_query, connection)
        connection.close()
    
    response.columns = [x.lower().replace('_', '-') for x in response.columns]
    
    curr_index = response.loc[(response['start-date'] <= pd.to_datetime(datetime.now()))].index[-1]
    
    response['actual-year-no'] = response.groupby('cal-year').ngroup()
    if cal_type in ['Q', 'P', 'W', 'D']:
        response['actual-quarter-no'] = response.groupby(['cal-year', 'quarter-no']).ngroup()    
    if cal_type in ['P', 'W', 'D']:
        response['actual-period-no'] = response.groupby(['cal-year', 'period-no']).ngroup()
    if cal_type in ['W', 'D']:
        response['actual-week-no'] = response.groupby(['cal-year', 'week-no']).ngroup()
    if cal_type == 'D':
        response['actual-day-no'] = response.groupby(['cal-year', 'day-no']).ngroup()    
    
    curr_day = response.loc[curr_index, 'actual-day-no'] if 'day-no' in response.columns else -1
    curr_week = response.loc[curr_index, 'actual-week-no'] if 'week-no' in response.columns else -1
    curr_period = response.loc[curr_index, 'actual-period-no'] if 'period-no' in response.columns else -1
    curr_quarter = response.loc[curr_index, 'actual-quarter-no'] if 'quarter-no' in response.columns else -1
    curr_year = response.loc[curr_index, 'actual-year-no']

    actual_day, actual_week, actual_period, actual_quarter, actual_year = None, None, None, None, None     
    
    if type(day) == str and day == 'current' and 'actual-day-no' in response.columns:
        actual_day = [curr_day]
    if type(week) == str and week == 'current' and 'actual-week-no' in response.columns:
        actual_week = [curr_week]
    if type(period) == str and period == 'current' and 'actual-period-no' in response.columns:
        actual_period = [curr_period]
    if type(quarter) == str and quarter == 'current' and 'actual-quarter-no' in response.columns:
        actual_quarter = [curr_quarter]
    if type(cal_year) == str and cal_year == 'current' and 'actual-year-no' in response.columns:
        actual_year = [curr_year]
        
    if type(day) == str and bool(re.match('^next [0-9]+$', day)) and 'actual-day-no' in response.columns:
        actual_day = list(range(response.loc[curr_index, 'actual-day-no'] + 1,
                                 response.loc[curr_index, 'actual-day-no'] + 1 + int(day.split()[1])))
    if type(week) == str and bool(re.match('^next [0-9]+$', week)) and 'actual-week-no' in response.columns:
        actual_week = list(range(response.loc[curr_index, 'actual-week-no'] + 1,
                                 response.loc[curr_index, 'actual-week-no'] + 1 + int(week.split()[1])))
    if type(period) == str and bool(re.match('^next [0-9]+$', period)) and 'actual-period-no' in response.columns:
        actual_period = list(range(response.loc[curr_index, 'actual-period-no'] + 1,
                                   response.loc[curr_index, 'actual-period-no'] + 1 + int(period.split()[1])))
    if type(quarter) == str and bool(re.match('^next [0-9]+$', quarter)) and 'actual-quarter-no' in response.columns:
        actual_quarter = list(range(response.loc[curr_index, 'actual-quarter-no'] + 1,
                                    response.loc[curr_index, 'actual-quarter-no'] + 1 + int(quarter.split()[1])))
    if type(cal_year) == str and bool(re.match('^next [0-9]+$', cal_year)) and 'actual-year-no' in response.columns:
        actual_year = list(range(response.loc[curr_index, 'actual-year-no'] + 1,
                                     response.loc[curr_index, 'actual-year-no'] + 1 + int(cal_year.split()[1])))
        
    if type(day) == str and bool(re.match('^last [0-9]+$', day)) and 'actual-day-no' in response.columns:
        actual_day = list(range(response.loc[curr_index, 'actual-day-no'] - 1,
                                 response.loc[curr_index, 'actual-day-no'] - 1 -int(day.split()[1]), -1))
    if type(week) == str and bool(re.match('^last [0-9]+$', week)) and 'actual-week-no' in response.columns:
        actual_week = list(range(response.loc[curr_index, 'actual-week-no'] - 1,
                                 response.loc[curr_index, 'actual-week-no'] - 1 -int(week.split()[1]), -1))
    if type(period) == str and bool(re.match('^last [0-9]+$', period)) and 'actual-period-no' in response.columns:
        actual_period = list(range(response.loc[curr_index, 'actual-period-no'] - 1,
                                   response.loc[curr_index, 'actual-period-no'] - 1 -int(period.split()[1]), -1))
    if type(quarter) == str and bool(re.match('^last [0-9]+$', quarter)) and 'actual-quarter-no' in response.columns:
        actual_quarter = list(range(response.loc[curr_index, 'actual-quarter-no'] - 1,
                             response.loc[curr_index, 'actual-quarter-no'] - 1 -int(quarter.split()[1]), -1))
    if type(cal_year) == str and bool(re.match('^last [0-9]+$', cal_year)) and 'actual-year-no' in response.columns:
        actual_year = list(range(response.loc[curr_index, 'actual-year-no'] - 1,
                                 response.loc[curr_index, 'actual-year-no'] - 1 - int(cal_year.split()[1]), -1))
        
    if actual_day is not None:
        response = response.loc[response['actual-day-no'].isin(actual_day)]
    if actual_week is not None:
        response = response.loc[response['actual-week-no'].isin(actual_week)]
    if actual_period is not None:
        response = response.loc[response['actual-period-no'].isin(actual_period)]
    if actual_quarter is not None:
        response = response.loc[response['actual-quarter-no'].isin(actual_quarter)]
    if actual_year is not None:
        response = response.loc[response['actual-year-no'].isin(actual_year)]
        
    if cal_year is not None and 'cal-year' in response.columns:     
        if type(cal_year) in [int, float]:
            response = response.loc[response['cal-year'] == cal_year]
        if type(cal_year) == list:
            response = response.loc[response['cal-year'].isin(cal_year)]
            
    if quarter is not None and 'quarter-no' in response.columns:
        if type(quarter) in [int, float]:
            response = response.loc[response['quarter-no'] == quarter]
        if type(quarter) == list:
            response = response.loc[response['quarter-no'].isin(quarter)]
            
    if period is not None and 'period-no' in response.columns:
        if quarter is not None:
            response['relative-period-no'] = response.groupby('actual-quarter-no')['period-no'].transform(lambda x: x - x.min() + 1)
        else:
            response['relative-period-no'] = response['period-no']
        if type(period) in [int, float]:
            response = response.loc[response['relative-period-no'] == period]
        if type(period) == list:
            response = response.loc[response['relative-period-no'].isin(period)]
    
    if week is not None and 'week-no' in response.columns:    
        if period is not None:
            response['relative-week-no'] = response.groupby('actual-period-no')['week-no'].transform(lambda x: x - x.min() + 1)
        elif quarter is not None:
            response['relative-week-no'] = response.groupby('actual-quarter-no')['week-no'].transform(lambda x: x - x.min() + 1)
        else:
            response['relative-week-no'] = response['week-no']
        if type(week) in [int, float]:
            response = response.loc[response['relative-week-no'] == week]
        if type(week) == list:
            response = response.loc[response['relative-week-no'].isin(week)]
            
    if day is not None and 'day-no' in response.columns:
        if week is not None:
            response['relative-day-no'] = response.groupby('actual-week-no')['day-no'].transform(lambda x: x - x.min() + 1)
        elif period is not None:
            response['relative-day-no'] = response.groupby('actual-period-no')['day-no'].transform(lambda x: x - x.min() + 1)
        elif quarter is not None:
            response['relative-day-no'] = response.groupby('actual-quarter-no')['day-no'].transform(lambda x: x - x.min() + 1)
        else:
            response['relative-day-no'] = response['day-no']
        if type(day) in [int, float]:
            response = response.loc[response['day-no'] == day]
        if type(day) == list:
            response = response.loc[response['day-no'].isin(day)]   
        
    if start_date is not None:
        response = response.loc[response['start-date'] >= start_date]
    if end_date is not None:
        response = response.loc[response['end-date'].fillna(response['start-date']) <= end_date]
    
    if calendar_id is not None:
        if type(calendar_id) in [int, float]:
            response = response.loc[response['calendar-id'] == calendar_id]
        if type(calendar_id) == list:
            response = response.loc[response['calendar-id'].isin(calendar_id)]
    
    return response.drop(columns = [x for x in ['actual-year-no', 'actual-quarter-no',
                                                'actual-period-no',
                                                'actual-week-no', 'actual-day-no',
                                                'relative-period-no', 'relative-week-no',
                                                'relative-day-no'] if x in response.columns])

# =============================================================================
# 
# =============================================================================

# For looking up product ids and levels, given either a name or some other partial info. Inputs described below:
# product_name -- a string or list of such to be matched, e.g. 'Upper Resp' or ['Upper Resp', 'Oral care']
# product_id -- a specific id or list of such, e.g. 1234 or [1234, 5678]
# product_level -- which level of product hierarchy, if known, e.g. 2 or 4
# retailer_item_code -- a specific retailer item code or list of such
# upc -- a specific upc or list of such
# hint -- a hint about which level of product hierarchy to search in, e.g. 'Item' or 'Category'
# exact_match -- set to False to disable exact matching on the name
# fuzzy_match -- set to False to disable fuzzy matching on the name
# contains -- set to False to disable substring matching on the name
# active -- 'Y', 'N', 'A'
# n -- Specifies the maximal number of responses you want or expect. Default is 1.

def prod_lookup(product_name = None, product_id = None, product_level = None,
                retailer_item_code = None, upc = None, hint = None,
                exact_match = True, fuzzy_match = True, contains = True, active = 'Y', n = 1):
    
    if product_name is None and product_id is None and retailer_item_code is None and upc is None:
        return pd.DataFrame(columns = ['product-id', 'product-level', 'product-name'])  
    
    if hint:
        syns = synonyms.loc[synonyms['type'] == 'prod'].copy(deep = True)
        hint_match = extractOne(hint,
                                list(syns['name'].values),
                                scorer = QRatio,
                                score_cutoff = 60)
        hint_match = hint_match[0] if hint_match else None
        if hint_match:
            product_level = int(syns.loc[syns['name'] == hint_match, 'level'].iloc[0])        
        
    if product_level is not None:
        if product_level == 1:
            query_list = [queries['item']]
        if product_level == 1.5:
            query_list = [queries['line-group']]
        if product_level >= 2:
            query_list = [queries['product-group']]
    elif retailer_item_code is not None or upc is not None:
        query_list = [queries['item']]
    else:
        query_list = [queries['product-group'], queries['line-group'], queries['item']]
        
    for query in query_list:
        if query == queries['product-group'] and 'product-groups' in product_data:
            response = product_data['product-groups'].copy(deep = True)
            if product_level is not None and product_level >= 2:
                response = response.loc[response['product-level'] == product_level]
        elif query == queries['line-group'] and 'line-groups' in product_data:
            response = product_data['line-groups'].copy(deep = True)
        elif query == queries['item'] and 'item-list' in product_data:
            response = product_data['item-list'].copy(deep = True)            
        else:
            connection = cx_Oracle.connect(username, password, dbname)
            response = pd.read_sql(query, connection)
            connection.close()            
            response.columns = [x.lower().replace('_', '-') for x in response.columns]
            
        if active in ['Y', 'N'] and 'active-indicator' in response.columns:
            response = response.loc[response['active-indicator'] == active]
    
        if product_id is not None:
            if type(product_id) in [int, float]:
                response = response.loc[response['product-id'] == product_id]
            if type(product_id) == list:
                response = response.loc[response['product-id'].isin(product_id)]
                
        if retailer_item_code is not None:
            if type(retailer_item_code) == str:
                response = response.loc[response['retailer-item-code'] == retailer_item_code]
            if type(retailer_item_code) == list:
                response = response.loc[response['retailer-item-code'].isin(retailer_item_code)]
                
        if upc is not None:
            if type(upc) == str:
                response = response.loc[response['upc'] == upc]
            if type(upc) == list:
                response = response.loc[response['upc'].isin(upc)]
                
        if upc or retailer_item_code or product_id:
            if not response.empty:
                return response.loc[:, ['product-id', 'product-level', 'product-name']].reset_index(drop = True)             
                
        if product_name is not None: 
            if type(product_name) == str:
                product_name = [product_name]
            if type(product_name) == list:
                results = []
                for p in product_name:
                    alias = re.sub(r'\s\s+', ' ', re.sub(r'[^a-zA-Z0-9]', ' ', p)).lower().strip()
                    matches = {'exact': None, 'fuzzy': None, 'contains': None}
                    if exact_match:
                        temp = response.loc[response['alias'] == alias]
                        if not temp.empty:
                            matches['exact'] = temp
                    if fuzzy_match and matches['exact'] is None:
                        sim = extractOne(alias,
                                         list(response['alias'].values),
                                         scorer = QRatio,
                                         score_cutoff = 85 if query == queries['product-group'] else 70)
                        if sim:
                            sim = [sim[0]]
                        else:
                            sim = []
                        temp = response.loc[response['alias'].isin(sim)]
                        if not temp.empty:
                            matches['fuzzy'] = temp
                    if contains and matches['exact'] is None and matches['fuzzy'] is None:
                        temp = response.loc[response['alias'].str.contains(alias)]
                        if not temp.empty:
                            matches['contains'] = temp
                            
                    if matches['exact'] is not None:
                        matches['exact'] = matches['exact'].sort_values(['product-level', 'product-name'], ascending = False)[0:n] 
                        results.append(matches['exact'].loc[:, ['product-id', 'product-level', 'product-name']])
                    elif matches['fuzzy'] is not None:
                        matches['fuzzy'] = matches['fuzzy'].sort_values(['product-level', 'product-name'], ascending = False)[0:n] 
                        results.append(matches['fuzzy'].loc[:, ['product-id', 'product-level', 'product-name']]) 
                    elif matches['contains'] is not None:
                        matches['contains'] = matches['contains'].sort_values(['product-level', 'product-name'], ascending = False)[0:n]   
                        results.append(matches['contains'].loc[:, ['product-id', 'product-level', 'product-name']])
                    else:
                        continue
                if len(results) > 0:
                    return pd.concat(results, ignore_index = True)
                else:
                    continue
        
    else:
        return pd.DataFrame(columns = ['product-id', 'product-level', 'product-name'])    
    
# =============================================================================
# 
# =============================================================================

# Aanalgous to the above but with locations instead of products.

def loc_lookup(location_name = None, location_id = None, location_level = None, hint = None,
               exact_match = True, fuzzy_match = True, contains = True, active = 'Y', n = 1):
    
    if location_name is None and location_id is None and location_level is None:
        return pd.DataFrame(columns = ['location-id', 'location-level', 'location-name'])
    
    if hint:
        syns = synonyms.loc[synonyms['type'] == 'loc'].copy(deep = True)
        hint_match = extractOne(hint,
                                list(syns['name'].values),
                                scorer = QRatio,
                                score_cutoff = 60)
        hint_match = hint_match[0] if hint_match else None
        if hint_match:
            location_level = int(syns.loc[syns['name'] == hint_match, 'level'].iloc[0])   
    
    response = location_data['list'].copy(deep = True)
    
    if active in ['Y', 'N']:
        response = response.loc[response['active-indicator'] == active]
    
    if location_level is not None:
        response = response.loc[response['location-level'] == location_level]
    
    if location_id is not None:
        if type(location_id) in [int, float]:
            response = response.loc[response['location-id'] == location_id]
        if type(location_id) == list:
            response = response.loc[response['location-id'].isin(location_id)]
        return response.loc[:, ['location-id', 'location-level', 'location-name']]
            
    if location_name is not None:            
        if type(location_name) == str:
            location_name = [location_name]
        if type(location_name) == list:
            results = []
            for p in location_name:
                alias = re.sub(r'\s\s+', ' ', re.sub(r'[^a-zA-Z0-9]', ' ', p)).lower().strip()
                
                s = alias.split()
                syns = synonyms.loc[synonyms['type'] == 'loc'].copy(deep = True)
                for word in s:
                    hint_match = extractOne(word,
                                            list(syns['name'].values),
                                            scorer = QRatio,
                                            score_cutoff = 80)
                    hint_match = hint_match[0] if hint_match else None
                    if hint_match:
                        location_level = int(syns.loc[syns['name'] == hint_match, 'level'].iloc[0])
                        response = response.loc[response['location-level'] == location_level]
                        
                matches = {'exact': None, 'fuzzy': None, 'contains': None}
                if exact_match:
                    temp = response.loc[response['alias'] == alias]
                    if not temp.empty:
                        matches['exact'] = temp
                if fuzzy_match:
                    sim = extractOne(alias,
                                     list(response['alias'].values),
                                     scorer = QRatio,
                                     score_cutoff = 60)
                    if sim:
                        sim = [sim[0]]
                    else:
                        sim = []
                    temp = response.loc[response['alias'].isin(sim)]
                    if not temp.empty:
                        matches['fuzzy'] = temp
                if contains:
                    temp = response.loc[response['alias'].str.contains(alias)]
                    if not temp.empty:
                        matches['contains'] = temp
                        
                if matches['exact'] is not None:
                    matches['exact'] = matches['exact'].sort_values(['location-level', 'location-name'], ascending = False)[0:n]  
                    results.append(matches['exact'].loc[:, ['location-id', 'location-level', 'location-name']])
                elif matches['fuzzy'] is not None:
                    matches['fuzzy'] = matches['fuzzy'].sort_values(['location-level', 'location-name'], ascending = False)[0:n]  
                    results.append(matches['fuzzy'].loc[:, ['location-id', 'location-level', 'location-name']]) 
                elif matches['contains'] is not None:
                    matches['contains'] = matches['contains'].sort_values(['location-level', 'location-name'], ascending = False)[0:n]
                    results.append(matches['contains'].loc[:, ['location-id', 'location-level', 'location-name']])
                else:
                    continue
            if len(results) > 0:
                return pd.concat(results, ignore_index = True)
            else:
                return pd.DataFrame(columns = ['location-id', 'location-level', 'location-name'])    

# =============================================================================
# 
# =============================================================================

# Helper function for fetching which products a user is authorized to see.

def get_user_prod(user_id):
    user_query = """
    select
        value
    from user_task
    where task_id = 5
    and value_type = 'PRODUCT_LIST'
    and user_id = '{}'
    """.format(user_id)
    
    connection = cx_Oracle.connect(username, password, dbname)
    response = pd.read_sql(user_query, connection)
    connection.close()
    
    if response.empty:
        return dict()

    result = dict()
    
    for entry in json.loads(response['VALUE'].iloc[0]):
        if int(entry['p-l-i']) in result:
            result[int(entry['p-l-i'])].append(int(entry['p-i']))
        else:
            result[int(entry['p-l-i'])] = [int(entry['p-i'])]
            
    return result

# =============================================================================
# 
# =============================================================================

# Wrapper function. Does the product lookup, checks authorization, and defaults to either ALL PRODUCTS  or list of authroized products if none specified.

def parse_prod_request(product_name = None, product_id = None, product_level = None,
                       user_id = None, active = 'Y', n = 1):
    
    auth_prod = {99: [all_prod_id]}
    if user_id is not None and user_id != 'ejack':
        auth_prod = get_user_prod(user_id)
        if len(auth_prod) == 0:
            raise ValueError('User has no authorized products.')  
        if 99 in auth_prod:
            auth_prod = {99: [all_prod_id]}
            
    if product_name is None and product_id is None:
        if 99 in auth_prod:
            temp = pd.DataFrame(columns = ['product-id', 'product-level', 'product-name'])
            temp['product-id'] = [all_prod_id]
            temp['product-level'] = 99
            temp['product-name'] = 'ALL PRODUCTS'
        else:
            product_id = []
            for p in auth_prod:
                product_id += auth_prod[p]
            temp = prod_lookup(product_id = product_id)
        temp['authorized'] = True
            
    else:
        temp = prod_lookup(product_name = product_name, product_id = product_id, product_level = product_level, n = n)
        temp['authorized'] = False
        
        if 99 in auth_prod:
            temp['authorized'] = True
        else:
            for p in auth_prod:
                if temp['authorized'].all():
                    break
                col_name = product_data['types'].loc[product_data['types']['product-level'] == p, 'product-type'].iloc[0]
                col_name = col_name.replace('_', '-') + '-id'
                lookup = product_data['hierarchy'].loc[product_data['hierarchy'][col_name].isin(auth_prod[p])]
                for i, row in temp.loc[temp['product-level'] <= p].iterrows():
                    if row.loc['product-level'] > 1.5: 
                        col_name = product_data['types'].loc[product_data['types']['product-level'] == row.loc['product-level'], 'product-type'].iloc[0]
                        col_name = col_name.replace('_', '-') + '-id'
                    elif row.loc['product-level'] == 1.5: 
                        col_name = 'ret-lir-id'
                    elif row.loc['product-level'] == 1:
                        col_name = 'item-code'
                    temp.loc[i, 'authorized'] = row.loc['product-id'] in lookup[col_name].values
        
        temp = temp.drop_duplicates()
    return temp

# =============================================================================
# 
# =============================================================================

# Wrapper function. Similar to above but with locations instead of products.
def parse_loc_request(location_name = None, location_id = None, location_level = None,
                      active = 'Y', n = 1):
    
    if location_name is None and location_id is None:
        temp = pd.DataFrame(columns = ['location-id', 'location-level', 'location-name'])
        temp['location-id'] = [chain_id]
        temp['location-level'] = 1
        temp['location-name'] = 'CHAIN'
    else:    
        temp = loc_lookup(location_name = location_name, location_id = location_id,
                          location_level = location_level, active = active, n = n)
        if ((temp['location-level'] == 6) & (temp['location-id'] == global_zone_id)).any():
            temp.loc[(temp['location-level'] == 6)
                     & (temp['location-id'] == global_zone_id), ['location-id',
                                                                 'location-level',
                                                                 'location-name']] = [chain_id, 1, 'CHAIN']        
    return temp

# =============================================================================
# 
# =============================================================================

# For querying the tlog. Not used by LLM currently.
def get_tlog(start_date, end_date, start_time = None, end_time = None,
             product_level = None, product_name = None, product_id = None,
             customer_id = None, store_id = None, **kwargs):
    
    start = pd.to_datetime(start_date).strftime('%d-%b-%y').upper()
    end = pd.to_datetime(end_date).strftime('%d-%b-%y').upper()
    
    cal = cal_lookup(start_date = start, end_date = end, cal_type = 'D')
    cal_ids = ', '.join([str(x) for x in cal['calendar-id']])
    
    cols = """
    trx_no,
    trx_time,
    store_id,
    customer_id,
    item_name,
    item_code,
    item_size,
    uom_name uom,
    ret_lir_name,
    ret_lir_id,
    brand_name, 
    brand_id,
    """
    
    for j, row in product_data['types'].iterrows():
        cols += """
        {p}_name,
        {p}_id,""".format(p = row['product-type'])
        
    cols += """
    quantity,
    net_amt
    """
        
    query = """select 
      {columns}
    from transaction_log tlog
    left join ({idv}) idv
      on idv.item_code = tlog.item_id
    where calendar_id in ({cal})""".format(columns = cols, idv = queries['idv'], cal = cal_ids)
    
    if type(customer_id) == int:
        query = query + '\n' + 'and customer_id = {}'.format(customer_id)
    if type(customer_id) == list:
        customer_ids = ', '.join([str(x) for x in customer_id])
        query = query + '\n' + 'and customer_id in ({})'.format(customer_ids)
        
    if type(store_id) == int:
        query = query + '\n' + 'and store_id = {}'.format(store_id)
    if type(store_id) == list:
        store_ids = ', '.join([str(x) for x in store_id])
        query = query + '\n' + 'and store_id in ({})'.format(store_ids)    
      
    for kw in kwargs:
        if type(kwargs[kw]) == str:
            query = query + '\n' + "and {} = '{}'".format(kw, kwargs[kw].replace("'", "''"))
        else:
            query = query + '\n' + "and {} = {}".format(kw, kwargs[kw])
    
    #print('Executing query:\n\n' + query)
    #start = time.time()
    connection = cx_Oracle.connect(username, password, dbname)
    tlog = pd.read_sql(query, connection)
    connection.close()
    #end = time.time()
    #print('Time taken: {} seconds'.format(round(end - start, 2)))
    
    if start_time is not None and end_time is not None:
        tlog.index = tlog['TRX_TIME']
        tlog = tlog.between_time(start_time, end_time).reset_index(drop = True)
                
    tlog['UNIT_PRICE'] = (tlog['NET_AMT'] / tlog['QUANTITY']).round(2)
    
    tlog.columns = [x.lower().replace('_', '-') for x in tlog.columns]
    
    return tlog

# =============================================================================
# 
# =============================================================================

# Get different views of product hierarchy by specifying product_id, product_level, and detail_level.

def prod_hier(product_name = None, product_id = None, product_level = None, detail_level = None, 
              other_levels = [], brands = False, active = 'Y', n = 1):
    
    if (product_id is None or product_level is None) and (product_name is not None or product_id is not None):
        prod = prod_lookup(product_name, product_id, product_level, n = n)
        if not prod.empty:
            product_id = [int(x) for x in prod['product-id']]
            product_level = float(prod['product-level'].max())
            product_name = None
    
    if detail_level is None and product_level is None:
        return None
    
    if detail_level is not None and product_level is None:
        product_level = detail_level

    if detail_level is None and product_level is not None:
        detail_level = product_level
        
    other_levels = [x for x in other_levels if x > detail_level] if other_levels != [] else other_levels
    
    if 'hierarchy' in product_data:
        if product_level >= 2:
            col_name = product_data['types'].loc[product_data['types']['product-level'] == product_level,
                                                 'product-type'].iloc[0]
            col_name = col_name.replace('_', '-') + '-id'
        elif product_level == 1.5:
            col_name = 'ret-lir-id'
        elif product_level == 1:
            col_name = 'item-code'
            
        if type(product_id) == int:
            lookup = product_data['hierarchy'].loc[product_data['hierarchy'][col_name] == product_id].copy(deep = True)
        elif type(product_id) == list:
            lookup = product_data['hierarchy'].loc[product_data['hierarchy'][col_name].isin(product_id)].copy(deep = True)
        elif product_id is None:
            lookup = product_data['hierarchy'].copy(deep = True)
        if active in ['Y', 'N']:
            lookup = lookup.loc[lookup['active-indicator'] == active]
        
        cols = []
        for j, row in product_data['types'].sort_values('product-level', ascending = False).iterrows():
            if row['product-level'] in other_levels + [product_level, detail_level]:
                cols += ['{prod}-name'.format(prod = row['product-type'].replace('_', '-'))]
                cols += ['{prod}-id'.format(prod = row['product-type'].replace('_', '-'))]
                
        if product_level >= 1.5 == detail_level:
            cols += ['product-name', 'product-id', 'product-level']
            lookup['product-name'] = np.where(lookup['ret-lir-id'].isna(), lookup['item-name'], lookup['ret-lir-name'])
            lookup['product-id'] = np.where(lookup['ret-lir-id'].isna(), lookup['item-code'], lookup['ret-lir-id'])
            lookup['product-level'] = np.where(lookup['ret-lir-id'].isna(), 1.0, 1.5)
            
        if product_level == 1.5 or 1.5 in other_levels:
            cols += ['ret-lir-name', 'ret-lir-id']
            
        if detail_level == 1:
            cols += ['item-name', 'item-code']
            
        if brands == True:
            cols += ['brand-name', 'brand-id']
            
        lookup = lookup.loc[:, cols].drop_duplicates().reset_index(drop = True)
        return lookup
            
    
    cols = ''
    
    for j, row in product_data['types'].sort_values('product-level', ascending = False).iterrows():
        if row['product-level'] in other_levels + [product_level, detail_level]:
            cols += """
            {prod}_name,
            {prod}_id,""".format(prod = row['product-type'])
        
    if product_level > 1.5 == detail_level:
        cols += """
        case
          when ret_lir_name is null then item_name
          else ret_lir_name
          end product_name,
        case
          when ret_lir_id is null then item_code
          else ret_lir_id
          end product_id,
        case
          when ret_lir_id is null then 1
          else 1.5
          end product_level,"""
          
    if product_level == 1.5 or 1.5 in other_levels:
        cols += """
        ret_lir_name,
        ret_lir_id,"""
        
    if detail_level == 1:
        cols += """
        item_name,
        item_code,"""
        
    if brands == True:
        cols += """
        brand_name,
        brand_id,"""
        
    cols = cols[:-1]

    hier_query = """
    select
        {}
    from ({})""".format(cols, queries['idv'])
    
    if active == 'Y':
        hier_query += "where active_indicator = 'Y' \n"
    elif active == 'N':
        hier_query += "where active_indicator = 'N' \n"
    else:
        hier_query += "where 0 = 0 \n"
    if product_id is not None:
        if product_level >= 2:
            hier_query += 'and {}_id'.format(product_data['types'].loc[product_data['types']['product-level'] == product_level,
                                            'product-type'].iloc[0])
        if product_level == 1.5:
            hier_query += 'and ret_lir_id'
        if product_level == 1:
            hier_query += 'and item_code'
        if type(product_id) in [int, float]:
            hier_query += ' = {}'.format(product_id)
        if type(product_id) == list:
            query_list = []
            q, r = len(product_id) // 1000, len(product_id) % 1000
            q = q + 1 if r > 0 else q
            for j in range(q):
                ids = ', '.join([str(int(x)) for x in product_id[1000 * j : 1000 * (j + 1)] if type(x) in [int, float]])
                query_list.append(hier_query + ' in ({})'.format(ids))
            hier_query = query_list
    
    if type(hier_query) == str:
        connection = cx_Oracle.connect(username, password, dbname)
        response = pd.read_sql(hier_query, connection)
        connection.close()
    if type(hier_query) == list:
        response = []
        for q in hier_query:
            connection = cx_Oracle.connect(username, password, dbname)
            response.append(pd.read_sql(q, connection))
            connection.close()
        response = pd.concat(response, ignore_index = True)            
    
    response.columns = [x.lower().replace('_', '-') for x in response.columns]
    response = response.drop_duplicates()    
    
    return response

# =============================================================================
# 
# =============================================================================

# Same as above but with locations instead of products. 

def loc_hier(location_name = None, location_id = None, location_level = None, detail_level = None, 
              other_levels = [], active = 'Y', n = 1):
    
    if (location_id is None or location_level is None) and (location_name is not None or location_id is not None):
        loc = loc_lookup(location_name, location_id, location_level, active = active, n = n)
        if not loc.empty:
            location_id = [int(x) for x in loc['location-id']]
            location_level = float(loc['location-level'].max())
            location_name = None
    
    if detail_level is None and location_level is None:
        return None
    
    if detail_level is not None and location_level is None:
        location_level = detail_level

    if detail_level is None and location_level is not None:
        detail_level = location_level
        
    other_levels = [x for x in other_levels if x > detail_level] if other_levels != [] else other_levels
    
    col_name = {1:'chain-id', 2:'division-id', 3:'region-id', 4:'district-id',
                5:'store-id', 6:'price-zone-id'}.get(location_level)
        
    if type(location_id) == int:
        lookup = location_data['hierarchy'].loc[location_data['hierarchy'][col_name] == location_id].copy(deep = True)
    elif type(location_id) == list:
        lookup = location_data['hierarchy'].loc[location_data['hierarchy'][col_name].isin(location_id)].copy(deep = True)
    elif location_id is None:
        lookup = location_data['hierarchy'].copy(deep = True)
    if active in ['Y', 'N']:
        lookup = lookup.loc[lookup['active-indicator'] == active]
    
    cols = []
    if 1 in other_levels + [location_level, detail_level]:
        cols += ['chain-id']
    if 2 in other_levels + [location_level, detail_level]:
        cols += ['division-id', 'division-no']
    if 3 in other_levels + [location_level, detail_level]:
        cols += ['region-id', 'region-no']
    if 4 in other_levels + [location_level, detail_level]:
        cols += ['district-id', 'district-no']
    if 5 in other_levels + [location_level, detail_level]:
        cols += ['store-id', 'store-no']
    if 6 in other_levels + [location_level, detail_level]:
        cols += ['price-zone-id', 'zone-no']
        
    lookup = lookup.loc[:, cols].drop_duplicates().reset_index(drop = True)
    return lookup
            
# =============================================================================
# 
# =============================================================================

# Function for getting item lists. Not currently used anywhere.

def get_item_list(product_id, product_level, active = 'Y'):
    item_query = """
    select
        child_product_id item_code
    from (
        select
            child_product_id, child_product_level_id
        from product_group_relation pgr
        start with product_level_id = {}
        and product_id = {}
        connect by prior child_product_level_id = product_level_id
        and prior child_product_id = product_id)
    where child_product_level_id = 1
    """.format(product_level, product_id)
    
    connection = cx_Oracle.connect(username, password, dbname)
    response = pd.read_sql(item_query, connection)
    connection.close()
    
    response.columns = [x.lower().replace('_', '-') for x in response.columns]
    return response

# =============================================================================
# 
# =============================================================================