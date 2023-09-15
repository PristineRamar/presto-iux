
import pickle
import numpy as np
from joblib import Parallel, delayed
import re
import difflib
from rapidfuzz import process
import pandas as pd
import time
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import dask.dataframe as dd
import requests
import os
from store.store_data_location import root_dir 
#common functions
def fuzzy_logic(df, name, n=1):
    # Create a new column 'alias' with lowercase store names
   # df['alias'] = df['Store_Name'].str.lower()

    # Check if name is an exact match to Store_Name
    exact_match = df[df['STORE_NAME'].str.lower() == name.lower()]
    if not exact_match.empty:
        return exact_match  # Return the filtered subset DataFrame

    # Apply fuzzy logic and find the closest match
    sim = process.extractOne(
    re.sub(r'[^a-zA-Z0-9]', ' ', name).lower(), df['ALIAS'], score_cutoff=0)

    #sim = difflib.get_close_matches(
       # re.sub(r'[^a-zA-Z0-9]', ' ', name).lower(), list(df['ALIAS'].values), n=n)
    if sim:
        closest_match = df[df['ALIAS'] == sim[0]]
        return closest_match  # Return the filtered subset DataFrame
    else:
        return None

# =========================================================================================


def fuzzy_logic2(df, store_name, n=1):
   try:
           ''' dict_path="C:\\Users\\Dell\\Desktop\\New folder\\custom_dict.txt"
            def read_text_file(file_path):
                with open(dict_path, 'r') as file:
                    return file.readlines()

            dictionary = read_text_file(dict_path)'''
           dictionary = ['CVS', 'Walgreen', 'Rite Aid', 'Walmart', 'Kroger', 'Dollar General', 'Safeway',
                        'Giant Eagle', 'Hy Vee', 'ShopRite', 'Stop & Shop', 'Home Depot', 'Lowes Home Improvement',
                        'Aldi', 'Wegmans', 'Weis Market', 'Publix', 'Winn Dixie',
                        'Price Chopper',  'Tops','Dollar tree', 'Grand Union', 'Tops Markets', 'Hannaford']
                  
           
           
          # dictionary = np.unique(df['STORE_NAME'].values)
           threshold =70   # Set your desired threshold value here
           best_match = process.extractOne(store_name, dictionary, score_cutoff=threshold)
           if best_match:
                best_match = best_match[0].strip()
           else:
                # Handle the case where no match meets the threshold
                best_match = None
           if best_match is not None:
            # Filter rows with a partial match to best_match using str.contains()
                banner_name_match = best_match.lower()
                filtered_df = df[df['STORE_NAME'].str.lower().str.contains(banner_name_match)]
                
           else:
            # Use fuzzy logic when best_match is None
                filtered_df = fuzzy_logic(df, store_name, n=1)
            
           return filtered_df
           #min_matching_letters = 3  # You can adjust this value as needed
          # filtered_df = filtered_df[filtered_df['STORE_NAME'].str.lower().apply(lambda x: x.startswith(store_name.lower()[:min_matching_letters]))]

   except:
          filtered_df = fuzzy_logic(df, store_name, n=1)
          return filtered_df
#=======================================================================================      
def fuzzy_logic_loc(loc, df, column_name, keywords=None, score_cutoff=0):
    
    if column_name not in df.columns:
        raise ValueError(f"'{column_name}' is not a valid column name in the DataFrame.")
        
    exact_match = df[df[column_name].str.lower() == loc.lower()]
    if not exact_match.empty:
        return exact_match  # Return the filtered subset DataFrame

    df['ALIAS_loc']=df[column_name].str.lower()
    # Apply fuzzy logic and find the closest match
    sim = process.extractOne(
    re.sub(r'[^a-zA-Z0-9]', ' ', loc).lower(), df['ALIAS_loc'], score_cutoff=65)

   # sim = difflib.get_close_matches(
       # re.sub(r'[^a-zA-Z0-9]', ' ', name).lower(), list(df['ALIAS'].values), n=n)
    if sim:
        closest_match = df[df['ALIAS_loc'] == sim[0]]
        return closest_match  # Return the filtered subset DataFrame
    else:
        return None     

#==========================================================================================
def calculate_distances(store_data, dist_row, earth_radius_miles):
    lat1 = store_data['LAT'].values[:, np.newaxis]
    lon1 = store_data['LON'].values[:, np.newaxis]
    a = np.sin((dist_row['LAT'] - lat1) / 2) ** 2 + np.cos(lat1) * \
               np.cos(dist_row['LAT']) * \
                      np.sin((dist_row['LON'] - lon1) / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distances_miles = earth_radius_miles * c
    return distances_miles

#========================================================================================

def add_distances(filtered_data, dist_store_data_all):
    # Convert latitude and longitude from degrees to radians
    store_data=filtered_data
    store_data[['LAT', 'LON']] = np.radians(store_data[['LAT', 'LON']])
    dist_store_data_all[['LAT', 'LON']] = np.radians(
        dist_store_data_all[['LAT', 'LON']])

    earth_radius_miles = 3958.8 # Earth's radius in miles

    # Use joblib Parallel to calculate distances in parallel
    num_cores = 16  # os.cpu_count()
    distances_list = Parallel(n_jobs=num_cores)(
        delayed(calculate_distances)(store_data, row, earth_radius_miles)
        for _, row in dist_store_data_all.iterrows()
    )

    # Assign the distances as new columns to the store_data DataFrame
    for i, dist_row in enumerate(dist_store_data_all['NAME']):
        col_name = f'Distance_{dist_row}'
        store_data[col_name] = distances_list[i]
    
    return store_data

# =============================================================================================================


def load_pickle_file(file_path):
    try:
        with open(file_path, 'rb') as file:
            data = pickle.load(file)
        return data
    except FileNotFoundError:
        return None

    
def save_to_pickle(filename, data):
    with open(filename, 'wb') as file:
        pickle.dump(data, file)
        
#=============================================================================================
#this function creates a mapping of distances of store name and competitior and store the result as pickle file.
#It uses functions calculate distances and add_distances
def return_data_from_pickle(file_path, store_name, distance_stores, city='US', state='US', geography=None):
   
    with open(file_path, 'rb') as file:
        data = pickle.load(file)

    # Apply fuzzy logic to get the filtered data for store_name
    filtered_data = fuzzy_logic2(data, store_name, n=1)
    if filtered_data is None:
        print("No matching store found for the given store name.")
        return
   
    original_store_data=filtered_data

    result=pd.DataFrame()
    folder_path='store-distances\\'
  
    base_path = root_dir + folder_path
    
    if type(distance_stores) == str:
        distance_stores = [distance_stores]
  
    print("filtered_data", filtered_data.shape)
    for distance_store in distance_stores:
       filtered_data_new=original_store_data.copy()
       dist_store_data = fuzzy_logic2(data, distance_store, n=1)
       combined_store_name = filtered_data['STORE_NAME'].iloc[0] +'_'+ dist_store_data['STORE_NAME'].iloc[0]
       
       if city != 'US' or state != 'US' or geography is not None:
           filtered_data_new= add_distances(filtered_data_new, dist_store_data)
       else:
           
           filename = os.path.join(base_path, f"{combined_store_name}.pkl")
    
           pickle_data = load_pickle_file(filename)
           if pickle_data is None:
               filtered_data_new= add_distances(filtered_data_new, dist_store_data)
               save_to_pickle(filename, filtered_data_new)
              # Reset index for both DataFrames
               filtered_data_new.reset_index(drop=True, inplace=True)
               
           else:
                filtered_data_new=pickle_data
       print("filtered_data_new", filtered_data_new.shape)
         
       # Reset index for both DataFrames
       filtered_data_new.reset_index(drop=True, inplace=True)
       result.reset_index(drop=True, inplace=True)
    
      # Concatenate DataFrames along columns (axis=1)
       result = pd.concat([result, filtered_data_new.loc[:, ~filtered_data_new.columns.isin(result.columns)]], axis=1)
       result.index = original_store_data.index
       
    del pickle_data
    return result
   
  
#============================================================================================
def mode_with_multiple(data):
   mode_data = data.mode()
   return mode_data[0] if not mode_data.empty else ''

def calculate_cluster_summary(clustered_data, merged_cluster_data, within, cat_cols):
    
    cluster_summaries = []
    store_cluster_mapping = []
    if 'URBANICITY' not in cat_cols:
        clustered_data=clustered_data.drop(columns=['URBANICITY'])
        
    factor_columns = ['POPULATION_DENSITY', 'MEDIAN_INCOME', 'HOUSING_UNITS', 'URBANICITY']
 
    for cluster in clustered_data['Cluster'].unique():
        group = clustered_data[clustered_data['Cluster'] == cluster]
        
        # Filter columns starting with "Distance_"
        distance_columns = group.filter(like="Distance_")
        
        avg_distance_miles = (distance_columns.sum(axis=1) / distance_columns.notna().sum(axis=1)).mean()
        if np.isnan(avg_distance_miles):
            group_new = merged_cluster_data[merged_cluster_data['Cluster'] == cluster+1]
            distance_columns_new = group_new.filter(like='Distance_')
        
            # Find the minimum distance in each row
            min_distances = distance_columns_new.apply(lambda row: row.min(), axis=1)
            avg_distance_miles = min_distances.mean()
          

            
    
       
              
        # Calculate average of factor columns if present
        avg_factors = {col: int(group[col].mean()) for col in factor_columns if col in group and col != 'URBANICITY'}
        
        # Calculate mode of Urbanicity only if it's present in the factor columns
        if 'URBANICITY' in group.columns :
            mode_urbanicity = mode_with_multiple(group['URBANICITY']) if 'URBANICITY' in factor_columns else None
        else:
            mode_urbanicity=None
        # List of up to 5 names in the cluster
        cluster_names = group['NAME'].head(5).tolist()
        
        cluster_summary = {
            'Cluster': cluster + 1,
            'Store Count': len(group),
            'Avg. Distance (Miles)': round(avg_distance_miles, 1),
            **avg_factors,
            'Store Names': ', '.join(cluster_names),
        }
        
        if mode_urbanicity is not None:
            cluster_summary['Urbanicity (Mode)'] = mode_urbanicity
        cluster_summaries.append(cluster_summary)
        
        # Create name-cluster mapping for up to 5 names
        for name in cluster_names:
            store_cluster_mapping.append(
                {'Store Name': name, 'Cluster': cluster + 1, 'Name_Count': len(group)})
    
    # Convert cluster summaries to a DataFrame
    summary = pd.DataFrame(cluster_summaries)
   # summary.dropna(axis=1, how='all', inplace=True)
   
    summary = summary.sort_values(by='Cluster', ascending=True)
   
     
    return summary

#=============================================================================================


import pandas as pd
from sklearn.decomposition import SparsePCA
from sklearn.cluster import KMeans

def cluster_data(filtered_data, num_cols, cat_cols, no_of_groups, min_store, max_store, num_components=20):
    filtered_data = filtered_data.reset_index(drop=True)

    # Apply one-hot encoding on categorical columns using sparse=True
    encoded_data = pd.get_dummies(filtered_data[cat_cols], sparse=True)

    # Use Sparse PCA to reduce dimensionality of numerical columns
    numerical_data = filtered_data[num_cols]

    if num_components is None:
        num_components = min(numerical_data.shape[1])  # Use all components if not specified

    # Use Sparse PCA for dimensionality reduction
    sparse_pca = SparsePCA(n_components=num_components)

    # Fit Sparse PCA on numerical data
    pca_results = sparse_pca.fit_transform(numerical_data)

    # Convert PCA results to DataFrame
    pca_results_df = pd.DataFrame(pca_results, columns=[f'PC{i+1}' for i in range(num_components)])

    # Truncate encoded_data to match the number of rows in pca_results_df
    encoded_data = encoded_data.iloc[:len(pca_results_df)]

    # Concatenate the numerical columns after PCA
    encoded_data = pd.concat([encoded_data, pca_results_df], axis=1)

    # Apply K-means clustering
    kmeans = KMeans(n_clusters=no_of_groups, n_init=10, random_state=42)
    kmeans.fit(encoded_data)

    # Get the cluster labels
    cluster_labels = kmeans.labels_

    # Add the cluster labels to the filtered data
    filtered_data['Cluster'] = cluster_labels

    # Calculate the total number of stores in each cluster
    cluster_sizes = filtered_data.groupby('Cluster').size().reset_index()
    cluster_sizes = cluster_sizes.rename(columns={0: 'sizes'})

    # Filter clusters based on store count range
    valid_clusters = cluster_sizes[
        (cluster_sizes['sizes'] >= min_store) & (cluster_sizes['sizes'] <= max_store)]

    # Filter the data to keep only rows corresponding to valid clusters
    filtered_data = filtered_data[filtered_data['Cluster'].isin(valid_clusters['Cluster'])]

    # Drop duplicate names within each cluster
    filtered_data = filtered_data.drop_duplicates(subset=['Cluster', 'NAME', 'LAT', 'LON'])

    return filtered_data



'''def cluster_data(filtered_data, num_cols, cat_cols, no_of_groups,min_store, max_store ,num_components=20 ):
    filtered_data = filtered_data.reset_index(drop=True)

    # Apply one-hot encoding on categorical columns using sparse=True
    encoded_data = pd.get_dummies(filtered_data[cat_cols], sparse=True)

    # Use PCA to reduce dimensionality of numerical columns
    numerical_data = filtered_data[num_cols]
    # Determine the maximum valid number of components based on data dimensions
    max_components = min(numerical_data.shape)
    if num_components is None or num_components > max_components:
        num_components = max_components

    pca = PCA(n_components=num_components)

    # Fit PCA on entire numerical data
    pca_results = pca.fit_transform(numerical_data)

    # Convert PCA results to DataFrame
    pca_results_df = pd.DataFrame(
        pca_results, columns=[f'PC{i+1}' for i in range(num_components)])

    # Truncate encoded_data to match the number of rows in pca_results_df
    encoded_data = encoded_data.iloc[:len(pca_results_df)]

    # Concatenate the numerical columns after PCA
    encoded_data = pd.concat([encoded_data, pca_results_df], axis=1)

    # Apply K-means clustering
    kmeans = KMeans(n_clusters=no_of_groups, n_init=10, random_state=42)
    kmeans.fit(encoded_data)

    # Get the cluster labels
    cluster_labels = kmeans.labels_

    # Add the cluster labels to the filtered data
    filtered_data['Cluster'] = cluster_labels
    
    # Calculate the total number of stores in each cluster
    
    cluster_sizes = filtered_data.groupby('Cluster').size().reset_index()
    cluster_sizes = cluster_sizes.rename(columns={0: 'sizes'})
    #print("cluster_size", cluster_sizes)
    #print("2", filtered_data.shape)
    # Filter clusters based on store count range
    valid_clusters = cluster_sizes[
        (cluster_sizes['sizes'] >= min_store) & (cluster_sizes['sizes'] <= max_store)].index
    valid_clusters = pd.DataFrame(valid_clusters, columns=['Cluster'])
    #print("min-max", min_store, max_store)
   # print("3", filtered_data.shape)
    #print(valid_clusters)
    # Filter the data to keep only rows corresponding to valid clusters
    filtered_data = filtered_data[filtered_data['Cluster'].isin(valid_clusters['Cluster'])]
   # print("4", filtered_data1.shape)
    #print("unique cluster",filtered_data['Cluster'].unique())
    # Drop duplicate names within each cluster
    filtered_data = filtered_data.drop_duplicates(subset=['Cluster', 'NAME', 'LAT', 'LON'])
   # print("5", filtered_data2.shape)
    return filtered_data
'''
#=============================================================================================

# ====================================================================================================
def fix_urbanicity(factors):
    urbanicity_factors = ['rural', 'urban', 'suburban']
    updated_list = []

    for word in factors:
        word = word.strip(', ')
        if word in urbanicity_factors:
            updated_list.append('urbanicity')
        else:
            updated_list.append(word)

    # Drop duplicates using set and preserve the order using list comprehension
    updated_list = list(dict.fromkeys(updated_list))

    # print("Updated list:", updated_list)
    return updated_list

#==========================================================================================
def process_factor(zipcodes_data, filtered_data_new, factor_name, column_name, fill_value=0):
    # Create a new DataFrame with 'City' and the specified column_name from zipcodes_data
    zipcodes_grouped = zipcodes_data.dropna(subset=[column_name])[['CITY', column_name]].groupby('CITY').mean().reset_index()
    filtered_data_new = filtered_data_new.merge(zipcodes_grouped, on='CITY', how='left')
    return filtered_data_new

#================================================================================================

# Function to extract city from NAME column
def extract_city(name):
    parts = name.split('-')
    if len(parts) > 1:
        return parts[-1].strip()
    else:
        return np.nan
    
#==================================================================================================
def get_selected_factors(factors):
     factor_mapping = {
                 'population density': 'POPULATION_DENSITY',
                 'median income': 'MEDIAN_INCOME',
                 'housing units': 'HOUSING_UNITS'
     }
     selected_factors = [factor_mapping[factor] if factor in factor_mapping else factor for factor in factors]
     return selected_factors
 
#================================================================================================    
def add_new_factor_data(factors, filtered_data_new):
    factor_columns=[]
    
    # adding data of new factors like population density, median income etec
    
    if any(factor in factors for factor in ['population density', 'median income', 'housing units']):
        if 'population density' in factors:
            factor_columns.append('population density')
        if 'housing units' in factors:
            factor_columns.append('housing units')
        if 'median income' in factors:
            factor_columns.append('median income')

    # Load the zipcodes_data_all.pkl file
        filename='zipcodes_data_all.pkl'
        file_name= root_dir + filename
        with open(file_name, 'rb') as zipcodes_file:
               zipcodes_data = pickle.load(zipcodes_file)
               
               zipcodes_data = pd.DataFrame(zipcodes_data)
               zipcodes_data.columns = [column.upper() for column in zipcodes_data.columns]
           
        # Assuming you have defined factor_columns, filtered_data_new, and zipcodes_data
        for factor in factor_columns:
                if factor == 'population density':
                    filtered_data_new = process_factor(zipcodes_data, filtered_data_new, factor, 'POPULATION_DENSITY')
                elif factor == 'median income':
                    filtered_data_new =process_factor(zipcodes_data,filtered_data_new, factor, 'MEDIAN_INCOME')
                elif factor == 'housing units':
                    filtered_data_new =process_factor(zipcodes_data,filtered_data_new, factor, 'HOUSING_UNITS')
   
    return filtered_data_new

#######################################################################################################
######################################################################################################============================================================================================
#1st use case 

def fetch_search_results(query, api_key, cx):
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        results = response.json()
        return results
    except requests.exceptions.RequestException as e:
        print("Error: ", e)
        return None
    except ValueError as e:
        print("Error parsing JSON response:", e)
        return None


# ============================================================================================

# collecting store info from google, using google places API
def get_store_info(store_name, api_key, cx):
    # Query for search results
    query = f"How many {store_name} stores are there in USA"

    # Fetch search results
    results = fetch_search_results(query, api_key, cx)

    # Process the results
    if results:
        items = results.get('items', [])
        for item in items:
            store_info = item.get('snippet', '')
            if "There are" in store_info:
                # Find the start index of the answer line
                start_index = store_info.find("There are")
                # Find the end index of the answer line
                end_index = store_info.find("as of")
                # Extract the answer line and remove leading/trailing spaces
                answer_line = store_info[start_index:end_index].strip()
                # Remove the store name from the answer line
                # print(answer_line)
                # Use regular expression to find numbers in the string with commas
                numbers = re.findall(r'\d{1,9}(?:,\d{1,9})*', answer_line)
                res = int(numbers[0].replace(',', '')) if numbers else None
                print(res)
                return res
    # If numbers are found, return the first one, otherwise return 0
    return None

#===================================================================================
# returning count of stores from stored pickle file

def func_find_no_of_stores(file_path, banner_name, city, state):
    try:
       
        with open(file_path, 'rb') as file:
            df = pickle.load(file)
        banner_name_match = fuzzy_logic(df, banner_name)
        if city!='US':
            city_name_match=fuzzy_logic_loc(city, df, 'CITY')
            df=city_name_match
        if state!='US':
            state_name_match=fuzzy_logic_loc(state, df, 'STATE_NAME')
            df=state_name_match
        # Check if banner_name_match is not None before using it
        if banner_name_match is not None:
            # Retrieve the 'alias' value from the matched row
            banner_name_match = banner_name_match.iloc[0]['ALIAS']

        # Count the occurrences of the store name in the DataFrame
        count = df[df['STORE_NAME'].str.lower().str.contains(
            banner_name_match)].shape[0]

        return count
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

##########################################################################################################
###########################################################################################################
# 2nd use case  : Find no of csv stores in 1,3,5 files of walgreens. 
# It uses common functions return_data_from_pickle
def func_no_of_competing_stores(file_path, banner_name, competition, distance_within, city, state, nostore, geography): #pass distance_within as list like [3,5]
  
        stores_with_distances=pd.DataFrame()
        stores_with_distances = return_data_from_pickle(file_path, banner_name, competition)
        # Shortlist columns starting with 'Distance_'
     
        if city!='US':
            city_name_match=fuzzy_logic_loc(city, stores_with_distances, 'CITY')
            stores_with_distances=city_name_match
        if state!='US':
            state_name_match=fuzzy_logic_loc(state, stores_with_distances, 'STATE_NAME')
            stores_with_distances=state_name_match
            
        if geography != None:
            geo_name_match=fuzzy_logic_loc(geography, stores_with_distances, 'GEOGRAPHY')
            stores_with_distances=geo_name_match
        
            
        distance_columns = [
            col for col in stores_with_distances.columns if col.startswith('Distance_')]

        # Step 1: Convert the 'stores_with_distances' DataFrame to a Dask DataFrame
        stores_with_distances_dask = dd.from_pandas(
            stores_with_distances, npartitions=4)

        # Step 2: Shortlist columns starting with 'Distance_'
        distance_columns = [
            col for col in stores_with_distances_dask.columns if col.startswith('Distance_')]

       
        # Step 3: Convert the distances DataFrame to a NumPy array
        stores_distances_np = stores_with_distances_dask[distance_columns].to_dask_array(
            lengths=True).compute()

        # Step 4: Calculate the counts within each distance range using NumPy
       
        counts_within_ranges = {}

        if len(distance_within) == 1:
            dist = distance_within[0]
            if nostore==True:
                 count_sum = np.sum(np.all(stores_distances_np > dist, axis=1))
                 count_sum = stores_distances_np.shape[0] - count_sum
                 count_sum=int(np.int32(count_sum))
                 
            else:
                counts = np.sum(stores_distances_np <= dist, axis=0)
                count_sum=int(np.sum(counts))
          
            counts_within_ranges[f'0-{dist} miles'] = count_sum
        else:
            for i in range(len(distance_within)):
                lower_limit = 0 if i == 0 else distance_within[i-1]
                upper_limit = distance_within[i]
                
                if nostore==True:
                    # Count the number of rows where no value falls within the distance range
                    counts = np.sum((stores_distances_np < lower_limit) | (stores_distances_np > upper_limit), axis=1)
                    count_sum = int(np.sum(counts))
                    count_sum = stores_distances_np.shape[0] - count_sum
                    count_sum=int(np.int32(count_sum))
                   
                 
                else:
                   counts = np.sum((stores_distances_np >= lower_limit) & (stores_distances_np <= upper_limit), axis=0)
                   count_sum = int(np.sum(counts))
                   key = f'{lower_limit}-{upper_limit} miles'
                   counts_within_ranges[key] = count_sum

        return counts_within_ranges

       
       
############################################################################################
############################################################################################

#============================================================================================    
 

def func_group_stores_cluster(file_path, store_name, no_of_groups, distance_stores, factors, within, city, state, min_store, max_store):
    start1 = time.time()
    filtered_data_new=pd.DataFrame()
    #creating distance files 
    filtered_data_new=return_data_from_pickle(file_path, store_name, distance_stores)
    original_data=filtered_data_new
    within=within[0]
    filtered_data_new = filtered_data_new.apply(lambda col: col.apply(lambda x: x if pd.isna(x) or x <=within else np.nan) if col.name.startswith("Distance_") else col)
    # Count values greater than 0 and not NaN in columns starting with "Distance_"
    #counts = filtered_data_new.filter(like="Distance_").gt(0).notna().sum()
    if filtered_data_new['CITY'].isna().sum() > 0 :
        filtered_data_new['CITY'] = filtered_data_new.apply(lambda row: extract_city(row['NAME']) if pd.isna(row['CITY']) else row['CITY'], axis=1)

    num_cols = ['LAT', 'LON']
    cat_cols = ['STATE', 'CITY']
    
   
    factors = [factor.lower() for factor in factors]
    filtered_data_new = add_new_factor_data(factors, filtered_data_new)   
    factors= get_selected_factors(factors)
    
  
    for factor in factors:
        regex_pattern = re.compile(rf'^{factor}$', re.IGNORECASE)
        matched_columns = [
            col for col in filtered_data_new.columns if regex_pattern.match(col)]
        if len(matched_columns) > 0:
            for col in matched_columns:
                if filtered_data_new[col].dtype == 'O':
                    cat_cols.append(col)
                else:
                    num_cols.append(col)

    if len(filtered_data_new) < no_of_groups:
        print("Insufficient data to form the desired number of clusters.")
        return

   
    cat_cols=list(set(cat_cols))
    # Extract only the categorical columns mentioned in cat_cols
    categorical_data = filtered_data_new[cat_cols]
    if city!='US':
        city_name_match=fuzzy_logic_loc(city, filtered_data_new, 'CITY')
        filtered_data_new=city_name_match
    if state!='US':
        state_name_match=fuzzy_logic_loc(state, filtered_data_new, 'STATE_NAME')
        filtered_data_new=state_name_match
    
   
   # Combine NAME with the provided categorical factors for accurate uniqueness check
    filtered_data_new['COMBINED_NAME'] = filtered_data_new['NAME'] + \
        '_' + categorical_data.astype(str).agg('_'.join, axis=1)+ '_'+filtered_data_new['LAT'].astype(str)

   # Drop duplicates based on the combined key of NAME and categorical factors
    filtered_data_new.drop_duplicates(subset=['COMBINED_NAME'], inplace=True)
    
    num_cols=list(set(num_cols))
    
    # Replace NaN values with 0 in the numeric columns of filtered_data
    filtered_data_new[num_cols] = filtered_data_new[num_cols].fillna(0)
    
    
    # Apply K-means clustering
    try :
        clustered_data = cluster_data(
            filtered_data_new, num_cols, cat_cols, no_of_groups, min_store, max_store)
        end1 = time.time()-start1
        print("time taken for clustering :", round(end1, 2))
  
    except Exception as e:
    # Check if the error message suggests reducing the number of clusters
        error_message = str(e)
        if "smaller than n_clusters" in error_message:
            raise ValueError("Please reduce the number of clusters.")
        else:
            # If it's a different exception, re-raise it
            raise 
    
        
    merged_cluster_data = pd.merge(original_data, clustered_data[['NAME', 'LAT', 'LON', 'Cluster']], on=['NAME', 'LAT', 'LON'], how='left')
    merged_cluster_data['Cluster']=merged_cluster_data['Cluster']+1
    start2=time.time()
    cluster_summary= calculate_cluster_summary(clustered_data, merged_cluster_data, within, cat_cols)
    cluster_summary['Cluster'] = range(1, len(cluster_summary) + 1)
    end2=time.time()-start2
    print("time taken for cluster summary :", round(end2, 2))

  
   
    return cluster_summary

