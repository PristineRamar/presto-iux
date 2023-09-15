import cx_Oracle
from recommendation.util import connectionString

def getProducts():
    ##get the connection string 
    connection_string =connectionString()
    try:
        # Attempt to establish a connection
        connection = cx_Oracle.connect(connection_string)
        cursor = connection.cursor()
    
    # Execute an SQL query to fetch data
        #cursor.execute("SELECT UPPER(NAME),PRODUCT_ID FROM PRODUCT_GROUP WHERE ACTIVE_INDICATOR='Y'")
        cursor.execute("SELECT UPPER(NAME),PRODUCT_ID FROM PRODUCT_GROUP WHERE  PRODUCT_ID IN(SELECT  PRODUCT_ID  FROM PR_QUARTER_REC_HEADER WHERE product_level_id=4 and run_status='S'AND  START_CALENDAR_ID IN(9187,9186))")
        rows = cursor.fetchall()
        data_list = {}
        for row in rows:
           # Create a dictionary for the current row
           name, product_id = row
           data_list[name] = product_id
      
        cursor.close()
        connection.close()
        return data_list
    
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"Oracle Error: {error.code} - {error.message}")
  
      

def getZonesByName():
    
    connection_string =connectionString()
   
    try:
  
        connection = cx_Oracle.connect(connection_string)
        cursor = connection.cursor()
    
    # Execute an SQL query to fetch data
        cursor.execute("SELECT UPPER(NAME) AS ZONE_NAME,PRICE_ZONE_ID FROM RETAIL_PRICE_ZONE WHERE ACTIVE_INDICATOR='Y'")
        rows = cursor.fetchall()
        data_list = {}
        for row in rows:
           zone_name, price_zone_id = row
           data_list[zone_name] = price_zone_id
          
    
        cursor.close()
        connection.close()
        return data_list
    
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"Oracle Error: {error.code} - {error.message}")
 
     
   
    

def getUserDetails(userId):
    connection_string =connectionString()
    query="""SELECT USER_ID,PASSWORD FROM USER_DETAILS WHERE USER_ID = :1"""
    
    try:
        connection = cx_Oracle.connect(connection_string)
        cursor = connection.cursor()
        cursor.execute(query, (userId,))
        rows = cursor.fetchall()
        data = rows[0]
        data = {'UserId': data[0], 'Password': data[1]}
        return data  # Return the data_list
    except Exception as e:
      print(f"Error: {e}")
      return None
    
    


def getLatestRunId(product_id, product_level_id, location_id, location_level_id):
   
    connection_string =connectionString()
    query = """SELECT MAX(RUN_ID) FROM PR_QUARTER_REC_HEADER WHERE PRODUCT_ID = :1 AND PRODUCT_LEVEL_ID = :2 AND LOCATION_ID = :3 AND LOCATION_LEVEL_ID = :4"""
    
    try:
    # Attempt to establish a connection
        connection = cx_Oracle.connect(connection_string)
        cursor = connection.cursor()
        cursor.execute(query,(product_id, product_level_id, location_id, location_level_id))
        result = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return result[0] if result else None
    except Exception as e:
      print(f"Error: {e}")
      return None
  
def getCategoryLevelId():
    connection_string =connectionString()
    query = """SELECT PRODUCT_LEVEL_ID FROM PR_PRODUCT_GROUP_TYPE_REC WHERE NAME LIKE'Category%'"""
    
    try:
    # Attempt to establish a connection
        connection = cx_Oracle.connect(connection_string)
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return result[0] if result else None
    except Exception as e:
      print(f"Error: {e}")
      return None
    
    
def getZonesById():
    
    connection_string =connectionString()
       
    try:
      
        connection = cx_Oracle.connect(connection_string)
        cursor = connection.cursor()
    
    # Execute an SQL query to fetch data
        cursor.execute("SELECT ZONE_NUM AS ZONE_NUMBER,PRICE_ZONE_ID FROM RETAIL_PRICE_ZONE WHERE ACTIVE_INDICATOR='Y'")
        rows = cursor.fetchall()
        data_list = {}
        for row in rows:
           zone_num, price_zone_id = row
           data_list[zone_num] = price_zone_id
           
        cursor.close()
        connection.close()
       
        return data_list
    
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"Oracle Error: {error.code} - {error.message}")
        return None
    
       
    
    
    
