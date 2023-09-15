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
        idv.retailer_item_code,
        rc.start_date,
        rc.end_date,
        pi.product_level_id,
        ps.metric_type_id,
        ps.sales,
        ps.units,
        ps.gross_margin,
        pw.curr_units,
        pw.pred_mov_final_price,
        pw.revenue_final_price,
        pw.margin_final_price,
        pi.rec_offer_type,
        pi.rec_offer_value,
        pl.promo_type_name AS rec_promotion,
        pi.rec_sale_multiple,
        pi.rec_sale_price,
        idv.item_name,
        idv.ret_lir_name,
        idv.category_name
        FROM
        pr_int_rec_summary        ps
        JOIN pr_pm_recommended_items   pi ON pi.run_id = ps.run_id
        JOIN pm_promo_type_lookup      pl ON pl.promo_type_id = pi.rec_promo_type_id
        JOIN retail_calendar           rc ON rc.calendar_id = pi.week_calendar_id
        JOIN item_details_view         idv ON pi.product_id = idv.item_code
        JOIN pr_weekly_rec_item        pw ON pw.week_calendar_id = pi.week_calendar_id
          AND pw.run_id = pi.run_id
          AND pw.product_id = pi.product_id
        WHERE
        ps.run_id = 171788
        AND ps.cal_type = 'Q'
        AND ps.view_type_id = 3
        AND ps.metric_type_id IN (1,2,3)
        AND pi.product_level_id = 1 and  pw.curr_units>0 and pw.pred_mov_final_price>0 and  pw.revenue_final_price>0 and  pw.margin_final_price>0
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        connection.close()
        
        # Create a list of dictionaries for JSON serialization
        result = [
        {
        'retailer_item_code': row[0],
        'start_date': row[1].strftime('%m/%d/%Y'),
        'end_date': row[2].strftime('%m/%d/%Y'),
        'product_level_id': row[3],
        'metric_type_id': row[4],
        'sales': row[5],
        'units': row[6],
        'gross_margin': row[7],
        'CURR_UNITS': row[8],
        'PRED_MOV_FINAL_PRICE': row[9],
        'REVENUE_FINAL_PRICE': row[10],
        'MARGIN_FINAL_PRICE': row[11],
        'rec_offer_type': row[12],
        'REC_OFFER_VALUE': row[13],
        'rec_promotion': row[14],
        'rec_sale_multiple': row[15],
        'rec_sale_price': row[16],
        'item_name':row[17],
        'ret_lir_name':row[18],
        'category_name':row[19],
        }
        for row in rows
        ]
        existing_data_str = json.dumps({"Data": json.dumps(result)})
        
        # Convert the existing JSON string to a dictionary
        existing_data = json.loads(existing_data_str)
        
        additional_info = {
        "timeframe": ["2023/03/09 - 2023/12/02"],
        "locations": ["Global Zone"],
        "products": ["Cultured Dairy"]
        }
        
        # Update the existing dictionary with additional_info
        existing_data.update(additional_info)
        
        # Convert the merged dictionary back to a JSON string
        #formatted_json = json.dumps(existing_data)
        
       
        # Return the formatted JSON
        return existing_data

    except Exception as e:
        return ({'error': str(e)})
