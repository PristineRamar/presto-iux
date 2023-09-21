import cx_Oracle
#from flask import Flask, jsonify,request
import json
from bpr.util import connectionString





def suggest_promo_to_meet_goals(week, period,  quarter, location_name, location_id, product_name, product_id):
    try:
        # Establish a database connection (provide connection_string)
        connection_string = connectionString()
        connection = cx_Oracle.connect(connection_string)
        cursor = connection.cursor()
        print('suggest_promo_to_meet_goals')
        # Define your SQL query here
        query = """
        SELECT
        IDV.RETAILER_ITEM_CODE AS ITEM_CODE,
        IDV.ITEM_NAME,
        PI.REG_PRICE AS REGULAR_RETAIL,
        PI.ORIG_SALE_PRICE AS ORIGINAL_SALE_RETAIL,
        PI.REC_SALE_PRICE AS RECOMMENDED_SALE_RETAIL,
        PL.PROMO_TYPE_NAME AS RECOMMENDED_PROMOTION,
        PI.PRED_MOV_ORIG_PROMO AS CURRENT_UNITS,
        PI.PRED_MOV_REC_PROMO AS PREDICTED_UNITS,
        PI.PRED_SALES_ORIG_PROMO AS CURRENT_REVENUE,
        PI.PRED_SALES_REC_PROMO AS PREDICTED_REVENUE,
        PI.PRED_MARGIN_ORIG_PROMO AS CURRENT_MARGIN,
        PI.PRED_MARGIN_REC_PROMO AS PREDICTED_MARGIN,
        IDV.CATEGORY_NAME,
        RC.START_DATE AS WEEK_START_DATE,
        RC.END_DATE AS WEEK_END_DATE
        FROM
        PR_INT_REC_SUMMARY        PS
        JOIN PR_PM_RECOMMENDED_ITEMS   PI ON PI.RUN_ID = PS.RUN_ID
        JOIN PM_PROMO_TYPE_LOOKUP      PL ON PL.PROMO_TYPE_ID = PI.REC_PROMO_TYPE_ID
        JOIN RETAIL_CALENDAR           RC ON RC.CALENDAR_ID = PI.WEEK_CALENDAR_ID
        JOIN ITEM_DETAILS_VIEW         IDV ON PI.PRODUCT_ID = IDV.ITEM_CODE
        WHERE PI.RUN_ID IN( 173227,173024,172925,172875,171714,171496,171020) AND
        PS.CAL_TYPE = 'Q' AND PS.VIEW_TYPE_ID = 3 AND PS.METRIC_TYPE_ID IN (1)
        AND PI.PRODUCT_LEVEL_ID = 1 AND PI.REC_SALE_PRICE > 0
        AND PI.REC_SALE_PRICE <> PI.ORIG_SALE_PRICE 
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        connection.close()
        
        # Create a list of dictionaries for JSON serialization
        result = [
        {
        'ITEM_CODE': row[0],
        'ITEM_NAME':row[1],
        'REGULAR_RETAIL': row[2],
        'ORIGINAL_SALE_RETAIL': row[3],
        'RECOMMENDED_SALE_RETAIL': row[4],
        'RECOMMENDED_PROMOTION': row[5],
        'CURRENT_UNITS': row[6],
        'PREDICTED_UNITS': row[7],
        'CURRENT_REVENUE': row[8],
        'PREDICTED_REVENUE': row[9],
        'CURRENT_MARGIN': row[10],
        'PREDICTED_MARGIN': row[11],
        'CATEGORY_NAME': row[12],
        'WEEK_START_DATE': row[13].strftime('%m/%d/%Y'),
        'WEEK_END_DATE': row[14].strftime('%m/%d/%Y')
        }
        for row in rows
        ]
        existing_data_str = json.dumps({"Data": json.dumps(result)})
        
        # Convert the existing JSON string to a dictionary
        existing_data = json.loads(existing_data_str)
        
        additional_info = {
        "timeframe": ["2023/03/09 - 2023/12/02"],
        "locations": ["Global Zone"],
        "products": ["Dairy"]
        }
        
        existing_data.update(additional_info)
        print('SENDING--',existing_data)
       
        return existing_data

    except Exception as e:
        return ({'error': str(e)})
