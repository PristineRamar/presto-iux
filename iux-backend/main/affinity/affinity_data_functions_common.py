# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 13:26:14 2023

@author: Dan
"""

import pandas as pd
import numpy as np
import re
import time
from datetime import datetime
import cx_Oracle
import difflib
import json
from affinity_data_config import username, dbname, password, idv_query, prod_types, all_prod_id


# =============================================================================
# 
# =============================================================================

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
        cal_year = cal_year + ' 1' if cal_year in ['next', 'last'] else cal_year
        cal_year = int(cal_year) if cal_year.isnumeric() else cal_year
    if type(quarter) == str:
        quarter = quarter + ' 1' if quarter in ['next', 'last'] else quarter
        quarter = int(quarter) if quarter.isnumeric() else int(re.sub('Q', '', quarter)) if bool(re.match('Q[1-4]', quarter)) else quarter   
    if type(period) == str:
        period = period + ' 1' if period in ['next', 'last'] else period
        period = int(period) if period.isnumeric() else int(re.sub('P', '', period)) if bool(re.match('P[1-12]', period)) else period  
    if type(week) == str:
        week = week + ' 1' if week in ['next', 'last'] else week
        week = int(week) if week.isnumeric() else int(re.sub('W', '', week)) if bool(re.match('W[1-53]', week)) else week
    if type(day) == str:
        day = day + ' 1' if day in ['next', 'last'] else day
        day = int(day) if day.isnumeric() else int(re.sub('D', '', day)) if bool(re.match('D[1-366]', day)) else day
        
    return cal_year, quarter, period, week, day

# =============================================================================
# 
# =============================================================================

def cal_lookup(cal_year = None, quarter = None, period = None, week = None, day = None, 
               start_date = None, end_date = None, calendar_id = None, cal_type = 'W'):
    
    cal_year, quarter, period, week, day = sanitize_cal_input(cal_year, quarter, period, week, day) 
    
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
    
    curr_index = response.loc[(response['start-date'] <= pd.to_datetime(datetime.now()))
                              & (response['end-date'].fillna(response['start-date']
                                + pd.Timedelta('1D')) >= pd.to_datetime(datetime.now()))].index[0]
    
    response['actual-year-no'] = response.groupby('cal-year').ngroup()
    if cal_type in ['Q', 'P', 'W', 'D']:
        response['actual-quarter-no'] = response.groupby(['cal-year', 'quarter-no']).ngroup()    
    if cal_type in ['P', 'W', 'D']:
        response['actual-period-no'] = response.groupby(['cal-year', 'period-no']).ngroup()
    if cal_type in ['W', 'D']:
        response['actual-week-no'] = response.groupby(['cal-year', 'week-no']).ngroup()
    if cal_type == 'D':
        response['actual-day-no'] = response.groupby(['cal-year', 'day-no']).ngroup()    
    
    curr_day = response.loc[curr_index, 'day-no'] if 'day-no' in response.columns else -1
    curr_week = response.loc[curr_index, 'week-no'] if 'week-no' in response.columns else -1
    curr_period = response.loc[curr_index, 'period-no'] if 'period-no' in response.columns else -1
    curr_quarter = response.loc[curr_index, 'quarter-no'] if 'quarter-no' in response.columns else -1
    curr_year = response.loc[curr_index, 'cal-year']

    actual_day, actual_week, actual_period, actual_quarter, actual_year = None, None, None, None, None     
    
    if type(day) == str and day[0:4] == 'next' and 'actual-day-no' in response.columns:
        actual_day = list(range(response.loc[curr_index, 'actual-day-no'] + 1,
                                 response.loc[curr_index, 'actual-day-no'] + 1 + int(day.split()[1])))
        day = None 
    if type(week) == str and week[0:4] == 'next' and 'actual-week-no' in response.columns:
        actual_week = list(range(response.loc[curr_index, 'actual-week-no'] + 1,
                                 response.loc[curr_index, 'actual-week-no'] + 1 + int(week.split()[1])))
        week = None
    if type(period) == str and period[0:4] == 'next' and 'actual-period-no' in response.columns:
        actual_period = list(range(response.loc[curr_index, 'actual-period-no'] + 1,
                                   response.loc[curr_index, 'actual-period-no'] + 1 + int(period.split()[1])))
        period = None
    if type(quarter) == str and quarter[0:4] == 'next' and 'actual-quarter-no' in response.columns:
        actual_quarter = list(range(response.loc[curr_index, 'actual-quarter-no'] + 1,
                                    response.loc[curr_index, 'actual-quarter-no'] + 1 + int(quarter.split()[1])))
        quarter = None
    if type(cal_year) == str and cal_year[0:4] == 'next' and 'actual-year-no' in response.columns:
        actual_year = list(range(response.loc[curr_index, 'actual-year-no'] + 1,
                                     response.loc[curr_index, 'actual-year-no'] + 1 + int(cal_year.split()[1])))
        cal_year = None
        
    if type(day) == str and day[0:4] == 'last' and 'actual-day-no' in response.columns:
        actual_day = list(range(response.loc[curr_index, 'actual-day-no'] - 1,
                                 response.loc[curr_index, 'actual-day-no'] - 1 -int(day.split()[1]), -1))
        day = None       
    if type(week) == str and week[0:4] == 'last' and 'actual-week-no' in response.columns:
        actual_week = list(range(response.loc[curr_index, 'actual-week-no'] - 1,
                                 response.loc[curr_index, 'actual-week-no'] - 1 -int(week.split()[1]), -1))
        week = None
    if type(period) == str and period[0:4] == 'last' and 'actual-period-no' in response.columns:
        actual_period = list(range(response.loc[curr_index, 'actual-period-no'] - 1,
                                   response.loc[curr_index, 'actual-period-no'] - 1 -int(period.split()[1]), -1))
        period = None
    if type(quarter) == str and quarter[0:4] == 'last' and 'actual-quarter-no' in response.columns:
        actual_quarter = list(range(response.loc[curr_index, 'actual-quarter-no'] - 1,
                             response.loc[curr_index, 'actual-quarter-no'] - 1 -int(quarter.split()[1]), -1))
        quarter = None
    if type(cal_year) == str and cal_year[0:4] == 'last' and 'actual-year-no' in response.columns:
        actual_year = list(range(response.loc[curr_index, 'actual-year-no'] - 1,
                                 response.loc[curr_index, 'actual-year-no'] - 1 - int(cal_year.split()[1]), -1))
        cal_year = None          
        
    if day is not None and 'day-no' in response.columns:    
        if type(day) == str and day == 'current':
            response = response[(response['day-no'] == curr_day)
                                & (response['cal-year'] == curr_year)]    
        if type(day) in [int, float]:
            response = response.loc[response['day-no'] == day]
        if type(day) == list:
            response = response.loc[response['day-no'].isin(day)]
            
    if week is not None and 'week-no' in response.columns:    
        if type(week) == str and week == 'current':
            response = response[(response['week-no'] == curr_week)
                                & (response['cal-year'] == curr_year)]    
        if type(week) in [int, float]:
            response = response.loc[response['week-no'] == week]
        if type(week) == list:
            response = response.loc[response['week-no'].isin(week)]
            
    if period is not None and 'period-no' in response.columns:     
        if type(period) == str and period == 'current':
            response = response[(response['period-no'] == curr_period)
                                & (response['cal-year'] == curr_year)]    
        if type(period) in [int, float]:
            response = response.loc[response['period-no'] == period]
        if type(period) == list:
            response = response.loc[response['period-no'].isin(period)]
            
    if quarter is not None and 'quarter-no' in response.columns:        
        if type(quarter) == str and quarter == 'current':
            response = response[(response['quarter-no'] == curr_quarter)
                                & (response['cal-year'] == curr_year)]    
        if type(quarter) in [int, float]:
            response = response.loc[response['quarter-no'] == quarter]
        if type(quarter) == list:
            response = response.loc[response['quarter-no'].isin(quarter)]
            
    if cal_year is not None and 'cal-year' in response.columns:     
        if type(cal_year) == str and cal_year == 'current':
            response = response[response['cal-year'] == curr_year]    
        if type(cal_year) in [int, float]:
            response = response.loc[response['cal-year'] == cal_year]
        if type(cal_year) == list:
            response = response.loc[response['cal-year'].isin(cal_year)]
    
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
        
    if start_date is not None:
        response = response.loc[response['start-date'] >= start_date]
    if end_date is not None:
        response = response.loc[response['end-date'].fillna(response['start-date']) <= end_date]
    
    if calendar_id is not None:
        if type(calendar_id) in [int, float]:
            response = response.loc[response['calendar-id'] == calendar_id]
        if type(calendar_id) == list:
            response = response.loc[response['calendar-id'].isin(calendar_id)]
            
    if 'quarter-no' in response.columns:
        response['quarter-no'] = response['quarter-no'].fillna(-1).astype(int).replace(-1, np.nan)
    if 'period-no' in response.columns:
        response['period-no'] = response['period-no'].fillna(-1).astype(int).replace(-1, np.nan)     
    
    return response.drop(columns = [x for x in ['actual-year-no', 'actual-quarter-no', 'actual-period-no',
                                                'actual-week-no', 'actual-day-no'] if x in response.columns])


# =============================================================================
# 
# =============================================================================

def prod_lookup(product_name = None, product_id = None, product_level = None, retailer_item_code = None, upc = None,
                exact_match = True, fuzzy_match = True, contains = True, active = 'Y', n = 1):
    
    if product_name is None and product_id is None and product_level is None and retailer_item_code is None and upc is None:
        return pd.DataFrame(columns = ['product-id', 'product-level', 'product-name'])
    
    prod_group_query = """
    select 
        product_id, 
        product_level_id product_level,
        name product_name,
        LOWER(REGEXP_REPLACE(name, '[^0-9A-Za-z]', ' ')) alias
    from product_group
    """
    if active == 'Y':
        prod_group_query += "where active_indicator = 'Y'"
    if active == 'N':
        prod_group_query += "where active_indicator = 'N'"
    prod_group_query += """
    order by product_level_id desc, name
    """
    
    line_group_query = """
    select
        ret_lir_id product_id,
        1.5 as product_level,
        ret_lir_name product_name,
        LOWER(REGEXP_REPLACE(ret_lir_name, '[^0-9A-Za-z]', ' ')) alias
    from retailer_like_item_group
    where ret_lir_id in (select ret_lir_id from item_lookup where lir_ind = 'N')
    """
    
    item_query = """
    select
        item_code product_id,
        1 as product_level,
        item_name product_name,
        retailer_item_code,
        upc,
        LOWER(REGEXP_REPLACE(item_name, '[^0-9A-Za-z]', ' ')) alias
    from item_lookup
    """
    if active == 'Y':
        item_query += "where active_indicator = 'Y'"
    if active == 'N':
        item_query += "where active_indicator = 'N'"        
    
    if product_level is not None:
        if product_level == 1:
            queries = [item_query]
        if product_level == 1.5:
            queries = [line_group_query]
        if product_level >= 2:
            queries = [prod_group_query]
    elif retailer_item_code is not None or upc is not None:
        queries = [item_query]
    else:
        queries = [prod_group_query, line_group_query, item_query]
        
    for query in queries:
        #break
        connection = cx_Oracle.connect(username, password, dbname)
        response = pd.read_sql(query, connection)
        connection.close()
        
        response.columns = [x.lower().replace('_', '-') for x in response.columns]
    
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
                    matches = {'exact': None, 'fuzzy': None, 'contains': None}
                    if exact_match:
                        temp = response.loc[response['alias'] == p]
                        if not temp.empty:
                            matches['exact'] = temp
                    if fuzzy_match:
                        sim = difflib.get_close_matches(re.sub(r'[^a-zA-Z0-9]', ' ', p).lower(),
                                                        list(response['alias'].values),
                                                        n)
                        temp = response.loc[response['alias'].isin(sim)]
                        if not temp.empty:
                            matches['fuzzy'] = temp
                    if contains:
                        temp = response.loc[response['alias'].str.contains(re.sub(r'[^a-zA-Z0-9]', ' ', p).lower())]
                        if not temp.empty:
                            matches['contains'] = temp
                            
                    if matches['exact'] is not None:
                        matches['exact'] = matches['exact'].sort_values(['product-level', 'product-name'], ascending = False).iloc[0:n]   
                        results.append(matches['exact'].loc[:, ['product-id', 'product-level', 'product-name']])
                    elif matches['contains'] is not None:
                        matches['contains'] = matches['contains'].sort_values(['product-level', 'product-name'], ascending = False).iloc[0:n]   
                        results.append(matches['contains'].loc[:, ['product-id', 'product-level', 'product-name']])
                    elif matches['fuzzy'] is not None:
                        matches['fuzzy'] = matches['fuzzy'].sort_values(['product-level', 'product-name'], ascending = False).iloc[0:n]   
                        results.append(matches['fuzzy'].loc[:, ['product-id', 'product-level', 'product-name']]) 
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

def loc_lookup(location_name = None, location_id = None, location_level = None, active = 'Y', n = 1):
    
    if location_name is None and location_id is None and location_level is None:
        return pd.DataFrame(columns = ['location-id', 'location-level', 'location-name'])
    
    zone_query = """
    select 
        price_zone_id location_id, 
        6 as location_level,
        zone_num location_name,
        LOWER(REGEXP_REPLACE(zone_num, '[^0-9A-Za-z]', ' ')) alias1,
        LOWER(REGEXP_REPLACE(description, '[^0-9A-Za-z]', ' ')) alias2
    from retail_price_zone
    where zone_type = 'W'
    """ + "and active_indicator = 'Y'" if active == 'Y' else ""
    
    store_query = """
    select
        comp_str_id location_id,
        5 as location_level,
        name location_name,
        LOWER(REGEXP_REPLACE(name, '[^0-9A-Za-z]', ' ')) alias1,
        LOWER(REGEXP_REPLACE(addr_line1 || addr_line2, '[^0-9A-Za-z]', ' ')) alias2
    from competitor_store
    """ + "where active_indicator = 'Y'" if active == 'Y' else ""
    
    if location_level is not None:
        if location_level == 1:
            queries = [zone_query]
        if location_level == 6:
            queries = [zone_query]
        if location_level == 5:
            queries = [store_query]
    else:
        queries = [zone_query, store_query]
        
    for query in queries:
        #break
        connection = cx_Oracle.connect(username, password, dbname)
        response = pd.read_sql(query, connection)
        connection.close()
        
        response.columns = [x.lower().replace('_', '-') for x in response.columns]
    
        if location_id is not None:
            if type(location_id) in [int, float]:
                response = response.loc[response['location-id'] == location_id]
            if type(location_id) == list:
                response = response.loc[response['location-id'].isin(location_id)]    
                
        if location_name is not None:            
            sim = difflib.get_close_matches(re.sub(r'[^a-zA-Z0-9]', ' ', location_name).lower(),
                                            list(response['alias1'].fillna('').values),
                                            n, cutoff = 0.5)
            
            if len(sim) == 0:
                sim = difflib.get_close_matches(re.sub(r'[^a-zA-Z0-9]', ' ', location_name).lower(),
                                                list(response['alias2'].fillna('').values),
                                                n, cutoff = 0.5)
                response = response.loc[response['alias2'].isin(sim)]
            else:
                response = response.loc[response['alias1'].isin(sim)]
            
        if response.empty:
            continue
        else:            
            response = response.sort_values(['location-level', 'location-name'], ascending = False).iloc[0:n]            
            return response.loc[:, ['location-id', 'location-level', 'location-name']].reset_index(drop = True)
    
    else:
        return pd.DataFrame(columns = ['location-id', 'location-level', 'location-name'])
    

# =============================================================================
# 
# =============================================================================

def prod_hier(product_name = None, product_id = None, product_level = None, detail_level = None, 
              other_levels = [], brands = False, active = 'Y'):
    
    if (product_id is None or product_level is None) and (product_name is not None or product_id is not None):
        prod = prod_lookup(product_name, product_id, product_level)
        if not prod.empty:
            product_id = int(prod.loc[0, 'product-id'])
            product_level = float(prod.loc[0, 'product-level'])
            product_name = None
    
    if detail_level is None and product_level is None:
        return None
    
    if detail_level is not None and product_level is None:
        product_level = detail_level

    if detail_level is None and product_level is not None:
        detail_level = product_level
        
    other_levels = [x for x in other_levels if x > detail_level] if other_levels != [] else other_levels
    
    cols = ''
    
    for j, row in prod_types.sort_values('product-level', ascending = False).iterrows():
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
    from ({})""".format(cols, idv_query)
    
    if active == 'Y':
        hier_query += "where active_indicator = 'Y' \n"
    elif active == 'N':
        hier_query += "where active_indicator = 'N' \n"
    else:
        hier_query += "where 0 = 0 \n"
    if product_id is not None:
        if product_level >= 2:
            hier_query += 'and {}_id'.format(prod_types.loc[prod_types['product-level'] == product_level,
                                            'product-type'].iloc[0])
        if product_level == 1.5:
            hier_query += 'and ret_lir_id'
        if product_level == 1:
            hier_query += 'and item_code'
        if type(product_id) in [int, float]:
            hier_query += ' = {}'.format(product_id)
        if type(product_id) == list:
            queries = []
            q, r = len(product_id) // 1000, len(product_id) % 1000
            q = q + 1 if r > 0 else q
            for j in range(q):
                ids = ', '.join([str(int(x)) for x in product_id[1000 * j : 1000 * (j + 1)] if type(x) in [int, float]])
                queries.append(hier_query + ' in ({})'.format(ids))
            hier_query = queries
    
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

def parse_prod_request(product_name = None, product_id = None, product_level = None,
                       user_id = None, active = 'Y'):
    
    auth_prod = {99: [all_prod_id]}
    if user_id is not None:
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
        return temp
    
    else:
        temp = prod_lookup(product_name = product_name, product_id = product_id, product_level = product_level)
        temp['authorized'] = False
        
        if 99 in auth_prod:
            temp['authorized'] = True
        else:
            for p in auth_prod:
                if temp['authorized'].all():
                    break
                lookup = prod_hier(product_id = auth_prod[p],
                                   product_level = p, detail_level = 1,
                                   active = active, other_levels = [l for l in [1, 1.5, 2, 3, 4, 5] if l <= p])
                for i, row in temp.iterrows():
                    if row.loc['product-level'] > 1.5: 
                        col_name = prod_types.loc[prod_types['product-level'] == row.loc['product-level'], 'product-type'].iloc[0] + '-id'
                    elif row.loc['product-level'] == 1.5: 
                        col_name = 'ret-lir-id'
                    elif row.loc['product-level'] == 1:
                        col_name = 'item-code'
                    temp.loc[i, 'authorized'] = row.loc['product-id'] in lookup[col_name].values
        
    return temp.loc[temp['authorized']].drop(columns = ['authorized']).drop_duplicates()


# =============================================================================
# 
# =============================================================================

def parse_loc_request(location_name = None, location_id = None, location_level = None):
    
    locations = dict()
    
    if (location_id is None or location_level is None) and location_name is not None:
        if type(location_name) == str:
            temp = loc_lookup(location_name, location_id, location_level)
            if not temp.empty:
                if int(temp.loc[0, 'location-level']) in locations:
                    locations[int(temp.loc[0, 'location-level'])].append((int(temp.loc[0, 'location-id']), temp.loc[0, 'location-name']))
                else:
                    locations[int(temp.loc[0, 'location-level'])] = [(int(temp.loc[0, 'location-id']), temp.loc[0, 'location-name'])]
        if type(location_name) == list:
            for p in location_name:
                temp = loc_lookup(location_name = p, location_id = location_id, location_level = location_level)
                if not temp.empty:
                    if int(temp.loc[0, 'location-level']) in locations:
                        locations[int(temp.loc[0, 'location-level'])].append((int(temp.loc[0, 'location-id']), temp.loc[0, 'location-name']))
                    else:
                        locations[int(temp.loc[0, 'location-level'])] = [(int(temp.loc[0, 'location-id']), temp.loc[0, 'location-name'])]
                        
    elif location_level is None and location_id is not None:
        if type(location_id) in [int, float]:
            temp = loc_lookup(location_id = location_id)
            if not temp.empty:
                if int(temp.loc[0, 'location-level']) in locations:
                    locations[int(temp.loc[0, 'location-level'])].append((int(temp.loc[0, 'location-id']), temp.loc[0, 'location-name']))
                else:
                    locations[int(temp.loc[0, 'location-level'])] = [(int(temp.loc[0, 'location-id']), temp.loc[0, 'location-name'])]
        if type(location_id) == list:
            for p in [int(x) for x in location_id if type(x) in [int, float]]:
                temp = loc_lookup(location_id = p)
                if not temp.empty:
                    if int(temp.loc[0, 'location-level']) in locations:
                        locations[int(temp.loc[0, 'location-level'])].append((int(temp.loc[0, 'location-id']), temp.loc[0, 'location-name']))
                    else:
                        locations[int(temp.loc[0, 'location-level'])] = [(int(temp.loc[0, 'location-id']), temp.loc[0, 'location-name'])]
                        
    elif location_id is not None and location_level is not None:
        if type(location_id) in [int, float]:
            locations[location_level] = [(int(location_id), 'NOT SPECIFIED')]
        if type(location_id) == list:
            locations[location_level] = [(int(x), 'NOT SPECIFIED') for x in location_id if type(x) in [int, float]]
            
    location_names = [t[1] for l in locations for t in locations[l]]
    location_ids = [t[0] for l in locations for t in locations[l]]
    locations = {l:[t[0] for t in locations[l]] for l in locations}
        
    return locations, location_names, location_ids


# =============================================================================
# 
# =============================================================================

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
    
    for j, row in prod_types.iterrows():
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
    where calendar_id in ({cal})""".format(columns = cols, idv = idv_query, cal = cal_ids)
    
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