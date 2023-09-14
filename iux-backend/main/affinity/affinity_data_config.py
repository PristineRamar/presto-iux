# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 13:27:34 2023

@author: Dan
"""
import pandas as pd
import cx_Oracle

chain_id = 52
global_zone_id = 1000
all_prod_id = 9491

username = 'PC_CSWG'
password = 'C#sW#Gp0rtStoProD'
dbname = 'secure5.pristineinfotech.com:6789/CSWG'
client_name = 'CS'
data_url = 'http://secure1.pristineinfotech.com:7200/presto-data-services'
#base_url = 'http://secure1.pristineinfotech.com:4200/presto-data-services'
is_db = False

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
# =============================================================================
# idv_query = """
# select 
#     item_code,
#     item_name,
#     retailer_item_code,
#     upc,
#     il.ret_lir_id,
#     lig.ret_lir_name,
#     item_size,
#     u.name as uom_name,
#     il.brand_id,
#     b.brand_name,
#     il.active_indicator,
#     segs.segment_id,
#     pg_s.name segment_name,
#     sub_cats.sub_category_id,
#     pg_sc.name sub_category_name,
#     cats.category_id,
#     pg_c.name category_name,
#     depts.department_id,
#     pg_d.name department_name
# from item_lookup il
# left join retailer_like_item_group lig
#     on il.ret_lir_id = lig.ret_lir_id
# left join uom_lookup u
#     on il.uom_id = u.id
# left join brand_lookup b
#     on il.brand_id = b.brand_id
# left join
#   (select 
#      child_product_id,
#      product_id segment_id
#    from product_group_relation
#    where child_product_level_id = 1
#    and product_level_id = 2
#   ) segs
# on segs.child_product_id = il.item_code
# left join product_group pg_s
#   on pg_s.product_id = segs.segment_id
#   and pg_s.product_level_id = 2
# left join
#   (select 
#      child_product_id,
#      product_id sub_category_id
#    from product_group_relation
#    where child_product_level_id = 2
#    and product_level_id = 3
#   ) sub_cats
# on sub_cats.child_product_id = segs.segment_id
# left join product_group pg_sc
#   on pg_sc.product_id = sub_cats.sub_category_id
#   and pg_sc.product_level_id = 3
# left join
#   (select 
#      child_product_id,
#      product_id category_id
#    from product_group_relation
#    where child_product_level_id = 3
#    and product_level_id = 4
#   ) cats
# on cats.child_product_id = sub_cats.sub_category_id
# left join product_group pg_c
#   on pg_c.product_id = cats.category_id
#   and pg_c.product_level_id = 4
# left join
#   (select
#      child_product_id,
#      product_id department_id
#    from product_group_relation
#    where child_product_level_id = 4
#    and product_level_id = 5
#   ) depts
# on depts.child_product_id = cats.category_id
# left join product_group pg_d
#   on pg_d.product_id = depts.department_id
#   and pg_d.product_level_id = 5
# """
# =============================================================================
