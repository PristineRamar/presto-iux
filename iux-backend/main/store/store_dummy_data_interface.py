# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 15:34:24 2023

@author: Dan
"""

from store.helper_functions_store_cluster import get_store_info, func_find_no_of_stores,func_no_of_competing_stores, func_group_stores_cluster
#change store.


###############################################################################################################
def find_no_of_stores(file_path, store_name, city, state, api_key, cx):
   try : 
       
        if store_name =="DG":
            store_name='Dollar General'
        if store_name=="GU":
            store_name='Grand Union'
            
        if city == 'US' and state =='US':
            store_info = get_store_info(store_name, api_key, cx)
        # print(store_info)
            if store_info is not None:
                        count = store_info
            else:
                count_of_stores = func_find_no_of_stores(file_path, store_name, city, state)
                if count_of_stores:
                        count = count_of_stores
         
        else:
             count_of_stores = func_find_no_of_stores(file_path, store_name, city, state)
             if count_of_stores:
                     count = count_of_stores
    
             else:
                raise ValueError("Store not found")
   
   except ValueError as e:
        print(e)
        count = 0
    
   return count


   

#=========================================================================================

# Find the nearest store for each competitor
def no_of_competing_stores(file_path, banner_name, competitions, distance_within, city, state, nostore, geography):
  
     counts_within_ranges = []
        
     for competition in competitions:
            count = func_no_of_competing_stores(file_path, banner_name, competition, distance_within, city, state, nostore, geography)
            counts_within_ranges.append({competition: count})  
       
     return counts_within_ranges
   

#========================================================================================
def group_stores_cluster(file_path, store_name, no_of_groups, distance_stores, factors, within, city, state, min_store, max_store):
   
    cluster_summary =func_group_stores_cluster(file_path, store_name, no_of_groups, distance_stores, factors,within, city, state, min_store, max_store)
    
    return cluster_summary

# ==========================================================================================================


