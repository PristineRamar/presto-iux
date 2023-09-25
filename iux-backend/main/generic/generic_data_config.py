# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 13:27:34 2023

@author: Dan
"""
import pandas as pd
import cx_Oracle
from config.app_config import config


# This code reads some basic information from the config, and then fetches
# and caches various views of the calendar, product hierarchy, and location hierarchy
# Optionally, cahcing can be toggled off in the config, though this is NOT recommended.
# In that case, the database will be queried on the fly when a user makes a request.

username = config["database"]["username"]
password = config["database"]["password"]
dbname = config["database"]["dbname"]
client_name = config["general"]["client_name"]
data_url = config["general"]["data_url"]
chain_id = config["general"]["chain_id"]
global_zone_id = config["general"]["global_zone_id"]
all_prod_id = config["general"]["all_prod_id"]
n_responses = config["general"]["n_responses"]
cache = config["general"]["cache"]
port = config["general"]["port"]
open_ai_key = config["open-ai"]["open_ai_key"]
log_filename = config["general"]["log_filename"]
comp_days = config["priceindex"]["comp_days"]
# =============================================================================
# username = 'READONLY_CSWG'
# password = 'RE1#AD2#CSWG'
# dbname = 'secure5.pristineinfotech.com:6789/CSWG'
# client_name = 'CNS'
# data_url = 'http://secure5.pristineinfotech.com:7200/presto-data-services'
# chain_id = 200
# global_zone_id = 1000
# all_prod_id = 9491
# n_responses = 5
# cache = True
# port = 4029
# open_ai_key = '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'
# log_filename = 'CS_STAGING'
# =============================================================================

# =============================================================================
# username = 'PRESTO_IUX'
# password = 'PR#IUX#2023'
# dbname = 'localhost:7781/IUX' #'secure7.pristineinfotech.com:7781/IUX'
# client_name = 'IUX'
# data_url = 'http://secure2.pristineinfotech.com:7800/presto-data-services'
# chain_id = 53
# global_zone_id = 483
# all_prod_id = 9491
# n_responses = 10
# cache = True
# port = 4028
# open_ai_key = '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'
# log_filename = 'SYN_STAGING'
# =============================================================================


# List of frequently-used synonyms for reference. Update as needed.
tuples = [('Day', 'cal', 0),
          ('Week', 'cal', 0),
          ('Period', 'cal', 0),
          ('Quarter', 'cal', 0),
          ('Year', 'cal', 0),
          ('Department', 'prod', 5),
          ('Major Category', 'prod', 5),
          ('Category', 'prod', 4),
          ('Sub-Category', 'prod', 3),
          ('Section', 'prod', 3),
          ('Segment', 'prod', 2),
          ('Item', 'prod', 1),
          ('Chain', 'loc', 1),
          ('Division', 'loc', 2),
          ('Region', 'loc', 3),
          ('District', 'loc', 4),
          ('Store', 'loc', 5),
          ('Zone', 'loc', 6)]
synonyms = pd.DataFrame(columns = ['name', 'type', 'level'], data = tuples)


# Fetching calendar data
cal_data = dict()

for cal_type in ['Y', 'Q', 'P', 'W', 'D']:
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
    cal_data[cal_type] = pd.read_sql(cal_query, connection)
    connection.close()


# Building product-related queries
type_query = """
select
    product_level_id product_level,
    child_product_level_id child_product_level,
    name product_type
from product_group_type
where 2 <= product_level_id and product_level_id <=99
start with product_level_id = 1
connect by prior product_level_id = child_product_level_id
order by product_level_id
"""

connection = cx_Oracle.connect(username, password, dbname)
prod_types = pd.read_sql(type_query, connection)
connection.close()
prod_types.columns = [x.lower().replace('_', '-') for x in prod_types.columns]
prod_types['product-type'] = prod_types['product-type'].str.replace(' ', '_').str.lower()

idv_cols = """
item_code,
item_name,
retailer_item_code,
upc,
il.ret_lir_id,
lig.ret_lir_name,
item_size,
u.name as uom_name,
il.brand_id,
b.brand_name,
il.active_indicator,
il.lir_ind,"""

for i, row in prod_types.iterrows():
    idv_cols += """
    pg_{}.name {}_name,
    {}.{}_id,""".format(row['product-type'], row['product-type'],
                        row['product-type'], row['product-type'])
    
idv_query = """
select
    {}
from item_lookup il
left join retailer_like_item_group lig
    on il.ret_lir_id = lig.ret_lir_id
left join uom_lookup u
    on il.uom_id = u.id
left join brand_lookup b
    on il.brand_id = b.brand_id""".format(idv_cols[:-1])
    
for i, row in prod_types.iterrows():
    j = 'il.item_code' if i == 0 else '{a}.{a}_id'.format(a = prod_types.loc[i - 1, 'product-type'])
    idv_query += """
    left join
      (select 
         child_product_id,
         product_id {prod_type}_id
       from product_group_relation
       where child_product_level_id = {child_level}
       and product_level_id = {prod_level}
      ) {prod_type}
    on {prod_type}.child_product_id = {join_col}
    left join product_group pg_{prod_type}
      on pg_{prod_type}.product_id = {prod_type}.{prod_type}_id
      and pg_{prod_type}.product_level_id = {prod_level}""".format(prod_type = row['product-type'],
                                                                   prod_level = row['product-level'],
                                                                   child_level = row['child-product-level'],
                                                                   join_col = j)
    
idv_query += """ where lir_ind = 'N'"""

prod_group_query = """
select 
    product_id, 
    product_level_id product_level,
    name product_name,
    TRIM(BOTH ' ' FROM LOWER(REGEXP_REPLACE(REGEXP_REPLACE(name, '[^0-9A-Za-z]', ' '), '[ ]{2,}', ' '))) alias,
    active_indicator
from product_group
"""
prod_group_query += """
where product_level_id in ({})
order by product_level_id desc, name
""".format(', '.join([str(x) for x in prod_types['product-level'].values]))

line_group_query = """
select
    ret_lir_id product_id,
    1.5 as product_level,
    ret_lir_name product_name,
    TRIM(BOTH ' ' FROM LOWER(REGEXP_REPLACE(REGEXP_REPLACE(ret_lir_name, '[^0-9A-Za-z]', ' '), '[ ]{2,}', ' '))) alias,
    'Y' as active_indicator
from retailer_like_item_group
where ret_lir_id in (select ret_lir_id from item_lookup where lir_ind = 'N' and active_indicator = 'Y')
union
select
    ret_lir_id product_id,
    1.5 as product_level,
    ret_lir_name product_name,
    TRIM(BOTH ' ' FROM LOWER(REGEXP_REPLACE(REGEXP_REPLACE(ret_lir_name, '[^0-9A-Za-z]', ' '), '[ ]{2,}', ' '))) alias,
    'N' as active_indicator
from retailer_like_item_group
where ret_lir_id in (select ret_lir_id from item_lookup where lir_ind = 'N' and active_indicator = 'N')
"""

item_query = """
select
    item_code product_id,
    1 as product_level,
    item_name product_name,
    retailer_item_code,
    upc,
    TRIM(BOTH ' ' FROM LOWER(REGEXP_REPLACE(REGEXP_REPLACE(item_name, '[^0-9A-Za-z]', ' '), '[ ]{2,}', ' '))) alias,
    active_indicator
from item_lookup
where lir_ind = 'N'
"""

# Building location-related queries

location_hierarchy_query = """
select
    comp_str_id store_id,
    comp_str_no store_no,
    cs.name store_name,
    rd.id district_id,
    rd.name district_no,
    rr.id as region_id,
    rr.name as region_no,
    rdiv.id as division_id,
    rdiv.name as divison_no,
    cs.comp_chain_id chain_id,
    pz.price_zone_id,
    pz.zone_num zone_no,
    cs.active_indicator
from competitor_store cs
left join retail_district rd
    on rd.id = cs.district_id
left join retail_region rr
    on rr.id = rd.region_id
left join retail_division rdiv
    on rdiv.id = rr.division_id
left join retail_price_zone pz
    on pz.price_zone_id = cs.price_zone_id
where cs.comp_chain_id = {}
""".format(chain_id)

connection = cx_Oracle.connect(username, password, dbname)
loc_hierarchy = pd.read_sql(location_hierarchy_query, connection)
connection.close()
loc_hierarchy.columns = [x.lower().replace('_', '-') for x in loc_hierarchy.columns]

location_list_query = """
select
    comp_str_id location_id,
    5 as location_level,
    name location_name,
    TRIM(BOTH ' ' FROM LOWER(REGEXP_REPLACE(REGEXP_REPLACE(name || ' ' || comp_str_no, '[^0-9A-Za-z]', ' '), '[ ]{2,}', ' '))) alias,
    active_indicator
from competitor_store cs
"""
location_list_query += 'where cs.comp_chain_id = {chain_id}'.format(chain_id = chain_id)
location_list_query += """
union
select 
    id location_id,
    4 as location_level,
    name location_name,
    TRIM(BOTH ' ' FROM LOWER(REGEXP_REPLACE(REGEXP_REPLACE('district' || ' ' || name, '[^0-9A-Za-z]', ' '), '[ ]{2,}', ' '))) alias,
    active_indicator
from retail_district
union
select 
    id location_id,
    3 as location_level,
    name location_name,
    TRIM(BOTH ' ' FROM LOWER(REGEXP_REPLACE(REGEXP_REPLACE('region' || ' ' || name, '[^0-9A-Za-z]', ' '), '[ ]{2,}', ' '))) alias,
    active_indicator
from retail_region
union
select 
    id location_id,
    2 as location_level,
    name location_name,
    TRIM(BOTH ' ' FROM LOWER(REGEXP_REPLACE(REGEXP_REPLACE('division' || ' ' || name, '[^0-9A-Za-z]', ' '), '[ ]{2,}', ' '))) alias,
    active_indicator
from retail_division
union
select 
    price_zone_id location_id, 
    6 as location_level,
    zone_num location_name,
    TRIM(BOTH ' ' FROM LOWER(REGEXP_REPLACE(REGEXP_REPLACE('zone' || ' ' || zone_num, '[^0-9A-Za-z]', ' '), '[ ]{2,}', ' '))) alias,
    active_indicator
from retail_price_zone 
where zone_type = 'W'
"""
location_list_query += """
union
select distinct
    {chain_id} as location_id,
    1 as location_level,
    'CHAIN' as location_name,
    'chain' as alias,
    'Y' as active_indicator
from retail_division
""".format(chain_id = chain_id)

connection = cx_Oracle.connect(username, password, dbname)
loc_list = pd.read_sql(location_list_query, connection)
connection.close()
loc_list.columns = [x.lower().replace('_', '-') for x in loc_list.columns]

# Caching the queries and location data
queries = {'product-hierarchy':idv_query, 'product-group':prod_group_query,
           'line-group':line_group_query, 'item':item_query,
           'location-hierarchy':location_hierarchy_query, 'location-list':location_list_query}
product_data = {'types':prod_types}
location_data = {'hierarchy':loc_hierarchy, 'list':loc_list}

# Caching the product data
if cache:
    connection = cx_Oracle.connect(username, password, dbname)
    hierarchy = pd.read_sql(idv_query, connection)
    connection.close()
    hierarchy.columns = [x.lower().replace('_', '-') for x in hierarchy.columns]
    product_data['hierarchy'] = hierarchy
    
    connection = cx_Oracle.connect(username, password, dbname)
    product_groups = pd.read_sql(prod_group_query, connection)
    connection.close()
    product_groups.columns = [x.lower().replace('_', '-') for x in product_groups.columns]
    product_data['product-groups'] = product_groups
    
    connection = cx_Oracle.connect(username, password, dbname)
    line_groups = pd.read_sql(line_group_query, connection)
    connection.close()
    line_groups.columns = [x.lower().replace('_', '-') for x in line_groups.columns]
    line_groups = line_groups.sort_values(by = ['product-id', 'product-name', 'active-indicator'])
    line_groups = line_groups.drop_duplicates(subset = ['product-id', 'product-name'], keep = 'last')
    product_data['line-groups'] = line_groups
    
    connection = cx_Oracle.connect(username, password, dbname)
    item_list = pd.read_sql(item_query, connection)
    connection.close()
    item_list.columns = [x.lower().replace('_', '-') for x in item_list.columns]
    product_data['item-list'] = item_list