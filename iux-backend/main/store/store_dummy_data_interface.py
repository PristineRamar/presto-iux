# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 15:34:24 2023

@author: Dan
"""

from store.helper_functions_store_cluster import get_store_info, func_find_no_of_stores,func_no_of_competing_stores, func_group_stores_cluster



###############################################################################################################
#find number of stores for each comeptitor
def find_no_of_stores(file_path, store_name, api_key, cx):
    
    store_info = get_store_info(store_name, api_key, cx)
    # print(store_info)
    if store_info is not None:
                count = store_info
    else:
        count_of_stores = func_find_no_of_stores(file_path, store_name)
        if count_of_stores:
            count = count_of_stores
        else:
            print("Please check store name")
            count = 0

    return count

#=========================================================================================

# Find the nearest store for each competitor
def no_of_competing_stores(file_path, banner_name, competition, distance_within):
  
       counts_within_ranges=func_no_of_competing_stores(file_path, banner_name, competition, distance_within)
    
       return counts_within_ranges
   

#========================================================================================
def group_stores_cluster(file_path, store_name, no_of_groups, distance_stores, factors, within=5):
   
    cluster_summary, clustered_data =func_group_stores_cluster(file_path, store_name, no_of_groups, distance_stores, factors)
    
    return cluster_summary, clustered_data

# ==========================================================================================================






# ===================================================================================================
# correct clustering code


'''def cluster_data(filtered_data, num_cols, cat_cols, no_of_groups, batch_size=1000, num_components=50):
    filtered_data = filtered_data.reset_index(drop=True)

    # Apply one-hot encoding on categorical columns using sparse=True
    encoded_data = pd.get_dummies(filtered_data[cat_cols], sparse=True)

    # Use Incremental PCA to reduce dimensionality of numerical columns
    numerical_data = filtered_data[num_cols]
    ipca = IncrementalPCA(n_components=num_components, batch_size=batch_size)

    # Initialize empty array to store PCA results
    pca_results = None

    # Process data in chunks
    for chunk_start in range(0, len(numerical_data), batch_size):
        chunk_end = min(chunk_start + batch_size, len(numerical_data))
        chunk_data = numerical_data.iloc[chunk_start:chunk_end]
        chunk_pca = ipca.partial_fit(chunk_data)
        chunk_result = chunk_pca.transform(chunk_data)

        # Concatenate PCA results from each chunk
        if pca_results is None:
            pca_results = chunk_result
        else:
            pca_results = np.concatenate((pca_results, chunk_result), axis=0)

   # Convert PCA results to DataFrame
    pca_results_df = pd.DataFrame(
        pca_results, columns=[f'PC{i+1}' for i in range(num_components)])

    # Truncate encoded_data to match the number of rows in pca_results_df
    encoded_data = encoded_data.iloc[:len(pca_results_df)]

    # Concatenate the numerical columns after IPCA
    encoded_data = pd.concat([encoded_data, pca_results_df], axis=1)

    # Apply K-means clustering
    kmeans = KMeans(n_clusters=no_of_groups)
    kmeans.fit(encoded_data)

    # Get the cluster labels
    cluster_labels = kmeans.labels_

    # Add the cluster labels to the filtered data
    filtered_data['Cluster'] = cluster_labels

    # Drop duplicate names within each cluster
    filtered_data = filtered_data.drop_duplicates(subset=['Cluster', 'NAME'])

    return filtered_data'''


'''def group_stores_cluster(file_path, store_name, no_of_groups, distance_stores, factors):
    start=time.time()
    with open(file_path, 'rb') as file:
        data = pickle.load(file)

    # Apply fuzzy logic to get the filtered data for store_name
    filtered_data = fuzzy_logic2(data, store_name, n=1)
    print("1", filtered_data.shape)
    print("1", filtered_data['Store_Name'].unique())
    if filtered_data is None:
        print("No matching store found for the given store name.")
        return
    # Load the distance store data
    dist_store_data_all = pd.DataFrame()
    for store in distance_stores:
        dist_store_data = fuzzy_logic2(data, store, n=1)
        print(dist_store_data.shape)
        if isinstance(dist_store_data, pd.DataFrame):
            dist_store_data_all = pd.concat(
                [dist_store_data_all, dist_store_data])

    # Drop any potential duplicates in the distance store data (if needed)
    dist_store_data_all.drop_duplicates(inplace=True)

    pickle_data = load_pickle_file('E:/Users/Chavi/stores_and_distances.pkl')
    # start2=time.time()
    # Check the data in pickle and decide which case it falls under
    case = check_data_in_pickle(
        filtered_data, dist_store_data_all, pickle_data)
    print(f"Case: {case}")

    if case == "case1":
        print("Using data from the pickle file.")
        # Use the data from the pickle file for filtered_data
        filtered_data_new = pickle_data.loc[pickle_data['NAME'].isin(
            filtered_data['NAME']), ~pickle_data.columns.str.startswith('Distance_')]

        # Include only the "dist_" columns that are present in dist_store_data_all
        dist_store_data_all_columns = [
            f"Distance_{col}" for col in dist_store_data_all['NAME'] if f"Distance_{col}" in pickle_data.columns]
        filtered_data_new = pd.concat([filtered_data_new, pickle_data.loc[pickle_data['NAME'].isin(
            filtered_data['NAME']), dist_store_data_all_columns]], axis=1)


    elif case == "case2":
        print("Using partial information from the pickle file.")
        # Use the data from the pickle file for filtered_data['NAME']
        filtered_data = pickle_data[pickle_data['NAME'].isin(
            filtered_data['NAME'])]

         # Create a list of dist_store_data names that are not present in the pickle file
        missing_dist_store_names = list(set(dist_store_data_all['NAME']) - set([col.replace(
            'Distance_', '') for col in pickle_data.columns if col.startswith('Distance_')]))

        # Create a DataFrame containing the missing dist_store_data names and their details
        missing_dist_store_data = dist_store_data_all[dist_store_data_all['NAME'].isin(
            missing_dist_store_names)]

        # Run add_distances for the missing dist_store_data and update the pickle file
        pickle_data=add_distances(filtered_data, missing_dist_store_data)

        # Update the pickle file with the new data
        # Include all columns except the "Distance_" columns in the final dataset
        # Include all columns without the "dist_" prefix
        filtered_data_new = pickle_data.loc[pickle_data['NAME'].isin(
            filtered_data['NAME']), ~pickle_data.columns.str.startswith('Distance_')]

        # Include only the "dist_" columns that are present in dist_store_data_all
        dist_store_data_all_columns = [
            f"Distance_{col}" for col in dist_store_data_all['NAME'] if f"Distance_{col}" in pickle_data.columns]
        filtered_data_new = pd.concat([filtered_data_new, pickle_data.loc[pickle_data['NAME'].isin(
            filtered_data['NAME']), dist_store_data_all_columns]], axis=1)

    else:  # case3
        print("Running add_distances for all and updating the pickle file.")
        # Run add_distances for all
        start=time.time()
        pickle_data=add_distances(filtered_data, dist_store_data_all)
        end=time.time()-start
        # Update the pickle file with the new data
        filtered_data_new= pickle_data

    if case!= "case1":
        # Save the updated pickle file
        with open('E:/Users/Chavi/stores_and_distances.pkl', 'wb') as file:
            pickle.dump(pickle_data, file)

   # Calculate distances and add them as new columns
    # add_distances(filtered_data, dist_store_data_all)

    # Save filtered_data as a pickle file
   # with open('C:/Users/Dell/iuxcodes/stores_and_distances.pkl', 'wb') as file:
      # pickle.dump(filtered_data, file)

    # Determine numerical and categorical columns based on factors using regex
    num_cols = filtered_data_new.select_dtypes(
        include='number').columns.tolist()
    cat_cols = []
    # factors_list = [word.strip() for word in factors]

   # factors= fix_urbanicity(factors_list)

    for factor in factors:
        regex_pattern = re.compile(rf'^{factor}$', re.IGNORECASE)
        matched_columns = [
            col for col in data.columns if regex_pattern.match(col)]
        if len(matched_columns) > 0:
            for col in matched_columns:
                if data[col].dtype == 'O':
                    cat_cols.append(col)
                else:
                    num_cols.append(col)

    if len(filtered_data) < no_of_groups:
        print("Insufficient data to form the desired number of clusters.")
        return

    # Apply K-means clustering
    clustered_data = cluster_data(
        filtered_data_new, num_cols, cat_cols, no_of_groups)

    # Group the store names by cluster
    groups = clustered_data.groupby('Cluster')['NAME'].apply(list)

     # Store the cluster information in a dictionary
    cluster_info = {}
    for cluster, stores in groups.items():
        cluster_name = f'Cluster_{cluster+1}'
        cluster_info[cluster_name] = stores
        print(f"\n{cluster_name} ({len(stores)} stores):")
        for store in stores:
            print(f"Store Name: {store}")
            # You can add more details about the store if available in the data
            # For example: print other columns like address, contact info, etc.

    # Print the number of stores in each cluster
    print("\nNumber of stores in each cluster:")
    for cluster, stores in groups.items():
        print(f"Cluster {cluster+1}: {len(stores)} stores")
    end=time.time()-start
    print("time taken in processing :", round(end,2))
    return cluster_info'''


#===================================================




# ==============================================================================================================

'''def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points on Earth given their latitudes and longitudes
    """
    R = 3958  # Earth's radius in miles
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * \
                 math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    distance_m = round(R * c, 2)

    return distance_m

def cluster_data(filtered_data, num_cols, cat_cols, no_of_groups):
    # Apply one-hot encoding on categorical columns
    encoded_data = pd.get_dummies(filtered_data[cat_cols])

    # Concatenate numerical columns
    encoded_data[num_cols] = filtered_data[num_cols]

    # Apply K-means clustering
    kmeans = KMeans(n_clusters=no_of_groups)
    kmeans.fit(encoded_data)

    # Get the cluster labels
    cluster_labels = kmeans.labels_

    # Add the cluster labels to the filtered data
    filtered_data['Cluster'] = cluster_labels

    # Drop duplicate names within each cluster
    filtered_data = filtered_data.drop_duplicates(subset=['Cluster', 'NAME'])
    # Calculate and print the silhouette score
   # silhouette_avg = silhouette_score(encoded_data, cluster_labels)
   # print("Silhouette Score:", silhouette_avg)

    return filtered_data


def fuzzy_logic2(df, store_name, n=1):
   try:
           ''dict_path="C:\\Users\\Dell\\Desktop\\New folder\\custom_dict.txt"
            def read_text_file(file_path):
                with open(dict_path, 'r') as file:
                    return file.readlines()''

            dictionary = read_text_file(dict_path
           dictionary=[' CVS',' Walgreen',' Rite Aid', ' Walmart',' Kroger',' Dollar General',' Safeway',
                        ' Giant Eagle',' Hy-Vee',' ShopRite',' Stop & Shop',' Home Depot',' Lowes Home Improvement',
                        ' Aldi', ' Wegmans',' Weis Market',' Publix',' Winn Dixie',
                        ' Price Chopper',' Tops Market',' Dollar tree']


            # Find the best match from the dictionary
           best_match = process.extractOne(store_name, dictionary)[0].strip()
            # Filter rows with a partial match to best_match using str.contains()
           # Convert best_match to lowercase for case-insensitive matching
           banner_name_match = best_match.lower()
           filtered_df = df[df['Store_Name'].str.lower(
           ).str.contains(banner_name_match)]

           return filtered_df
   except :
          filtered_df=fuzzy_logic(df, store_name, n=1)
          return filtered_df

def calculate_distances(filtered_data, dist_row, earth_radius_km):
    lat1 = filtered_data['LAT'].values[:, np.newaxis]
    lon1 = filtered_data['LON'].values[:, np.newaxis]
    a = np.sin((dist_row['LAT'] - lat1) / 2) ** 2 + np.cos(lat1) * \
               np.cos(dist_row['LAT']) * \
                      np.sin((dist_row['LON'] - lon1) / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distances_km = earth_radius_km * c
    return distances_km

def add_distances(filtered_data, dist_store_data_all):
    # Convert latitude and longitude from degrees to radians
    filtered_data[['LAT', 'LON']] = np.radians(filtered_data[['LAT', 'LON']])
    dist_store_data_all[['LAT', 'LON']] = np.radians(
        dist_store_data_all[['LAT', 'LON']])

    earth_radius_km = 6371.0  # Earth's radius in kilometers

    # Use joblib Parallel to calculate distances in parallel
    num_cores = 20 #os.cpu_count()
    distances_list = Parallel(n_jobs=num_cores)(
        delayed(calculate_distances)(filtered_data, row, earth_radius_km)
        for _, row in dist_store_data_all.iterrows()
    )

    # Assign the distances as new columns to the filtered_data DataFrame
    for i, dist_row in enumerate(dist_store_data_all['NAME']):
        col_name = f'Distance_{dist_row}'
        filtered_data[col_name] = distances_list[i]

    return filtered_data


def group_stores_cluster(file_path, store_name, no_of_groups, distance_stores, factors):
    with open(file_path, 'rb') as file:
        data = pickle.load(file)

    # Apply fuzzy logic to get the filtered data for store_name
    filtered_data = fuzzy_logic2(data, store_name, n=1)
    print("1", filtered_data.shape)
    print("1", filtered_data['Store_Name'].unique())
    if filtered_data is None:
        print("No matching store found for the given store name.")
        return

    # Load the distance store data
    dist_store_data_all = pd.DataFrame()
    for store in distance_stores:
        dist_store_data = fuzzy_logic2(data, store, n=1)
        if isinstance(dist_store_data, pd.DataFrame):
            dist_store_data_all = pd.concat(
                [dist_store_data_all, dist_store_data])

    # Drop any potential duplicates in the distance store data (if needed)
    dist_store_data_all.drop_duplicates(inplace=True)

    # Calculate distances and add them as new columns
    add_distances(filtered_data, dist_store_data_all)

    # Determine numerical and categorical columns based on factors using regex
    num_cols = filtered_data.select_dtypes(include='number').columns.tolist()
    cat_cols = []

    factors_list = [word.strip() for word in factors]

    factors= fix_urbanicity(factors_list)

    for factor in factors:
        regex_pattern = re.compile(rf'^{factor}$', re.IGNORECASE)
        matched_columns = [
            col for col in data.columns if regex_pattern.match(col)]
        if len(matched_columns) > 0:
            for col in matched_columns:
                if data[col].dtype == 'O':
                    cat_cols.append(col)
                else:
                    num_cols.append(col)

    if len(filtered_data) < no_of_groups:
        print("Insufficient data to form the desired number of clusters.")
        return

    # Apply K-means clustering
    clustered_data = cluster_data(
        filtered_data, num_cols, cat_cols, no_of_groups)

    # Group the store names by cluster
    groups = clustered_data.groupby('Cluster')['NAME'].apply(list)

     # Store the cluster information in a dictionary
    cluster_info = {}
    for cluster, stores in groups.items():
        cluster_name = f'Cluster_{cluster+1}'
        cluster_info[cluster_name] = stores
        print(f"\n{cluster_name} ({len(stores)} stores):")
        for store in stores:
            print(f"Store Name: {store}")
            # You can add more details about the store if available in the data
            # For example: print other columns like address, contact info, etc.

    # Print the number of stores in each cluster
    print("\nNumber of stores in each cluster:")
    for cluster, stores in groups.items():
        print(f"Cluster {cluster+1}: {len(stores)} stores")

    return cluster_info'''


'''def group_stores_cluster(file_path, store_name, no_of_groups, distance_stores, factors):
    with open(file_path, 'rb') as file:
        data = pickle.load(file)

    # Apply fuzzy logic to get the filtered data for store_name
    filtered_data = fuzzy_logic2(data, store_name, n=1)
   # print("1", filtered_data.shape)
    # print("1", filtered_data['Store_Name'].unique())
    if filtered_data is None:
        print("No matching store found for the given store name.")
        return

    # Include the distance stores in the filtered data
    for store in distance_stores:
        dist_store_data = fuzzy_logic2(data, store, n=1)
       # print("2", dist_store_data.shape)
       # print("2", dist_store_data['Store_Name'].unique())
        if dist_store_data is not None:
            filtered_data = pd.concat([filtered_data, dist_store_data])

    # Calculate distances and add them as new columns
    for store in distance_stores:
        filtered_data[f'Distance_{store}_LAT'] = filtered_data.apply(lambda row: haversine(
            row['LAT'], row['LON'], dist_store_data['LAT'].iloc[0], dist_store_data['LON'].iloc[0]), axis=1)
        filtered_data[f'Distance_{store}_LON'] = filtered_data.apply(lambda row: haversine(
            row['LAT'], row['LON'], dist_store_data['LAT'].iloc[0], dist_store_data['LON'].iloc[0]), axis=1)
        distance_lat_columns = [col for col in filtered_data.columns if col.startswith(
            'Distance_') and col.endswith('_LAT')]
        distance_lon_columns = [col for col in filtered_data.columns if col.startswith(
            'Distance_') and col.endswith('_LON')]

    # Determine numerical and categorical columns based on factors using regex
    # num_cols = ['LAT', 'LON'] + distance_lat_columns + distance_lon_columns
    num_cols =  distance_lat_columns + distance_lon_columns

    cat_cols = []

    factors_list = [word.strip() for word in factors]

    factors= fix_urbanicity(factors_list)


    for factor in factors:
        regex_pattern = re.compile(rf'^{factor}$', re.IGNORECASE)
        matched_columns = [
            col for col in data.columns if regex_pattern.match(col)]

        if len(matched_columns) > 0:
            for col in matched_columns:
                if data[col].dtype == 'O':
                    cat_cols.append(col)
                else:
                    num_cols.append(col)

    if len(filtered_data) < no_of_groups:
        print("Insufficient data to form the desired number of clusters.")
        return

    # Apply K-means clustering
    clustered_data = cluster_data(
        filtered_data, num_cols, cat_cols, no_of_groups)

    # Group the store names by cluster
    groups = clustered_data.groupby('Cluster')['NAME'].apply(list)

    # Store the cluster information in a dictionary
    cluster_info = {}
    for cluster, stores in groups.items():
        cluster_info[f'Cluster_{cluster+1}'] = stores

    # Print the number of stores in each cluster
   # print("\nNumber of stores in each cluster:")
   # for cluster, stores in groups.items():
    #    print(f"Cluster {cluster+1}: {len(stores)} stores")

    return cluster_info'''

# =============================================================================================================================


'''def cost_api(product_name=None, product_id=None, product_level=None, item_list=None, active='Y',
             location_name=None, location_id=None, location_level=None,
             cal_year=None, quarter=None, period=None, week=None, day=None,
             start_date=None, end_date=None, calendar_id=None, cal_type='W', user_id=None, change='A'):

    with open('sample_cost.json', 'r') as file:
        x = json.load(file)

    return pd.DataFrame(x['data']), x['products'], x['locations'], x['timeframe']'''

# =============================================================================
#
# =============================================================================





    # Save to Excel file with two tabs
'''excel_file = f'E:/Users/Chavi/cluster_results_{store_name}_{distance_stores}.xlsx'
    with pd.ExcelWriter(excel_file) as writer:
     summary_df.to_excel(writer, sheet_name='Summary', index=False)
     clustered_data.to_excel(writer, sheet_name='Clustered_Data', index=False)

    print(f"Summary and store-cluster mapping saved to {excel_file}")'''
#==========================================================================================
  
    



'''start= time.time()
file_path = 'E:/Users/Chavi/Competitor_Store.pkl'
store_name = 'aldi'
no_of_groups = 10
distance_stores = [ 'walmart', 'giant eagle']
factors = ['State', 'Urbanicity', 'Median Income']

x=group_stores_cluster(file_path, store_name, no_of_groups, distance_stores, factors)
print(x)
end=time.time()-start
print("time_taken : ", round(end, 2), "sec")'''


