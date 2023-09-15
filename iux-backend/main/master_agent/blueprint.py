# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 18:14:51 2023

@author: Dan
"""

from flask import Blueprint, Response, request, jsonify
import requests
from master_agent.flow import retriever, list_retriever, bm25_retriever
from config.app_config import config
router = config['router']
from fastapi import HTTPException
import httpx
import json
import cx_Oracle
import pandas as pd
from app_logger.logger import logger

controller_blueprint = Blueprint('controller', __name__)

def prompt2api(message, retriever):
    retrieved_nodes = retriever.retrieve(message)
    metadata = retrieved_nodes[0].node.metadata
    api_name = metadata['title']
    return api_name 

# =============================================================================
# def get_conv_history(user_id, session_id):
#     query = """select message from conversations
#     where userdetails = '{}' and sessionid = '{}'
#     order by timestamp""".format(user_id, session_id)
#     connection = cx_Oracle.connect(convo_username, convo_password, convo_dbname)
#     response = pd.read_sql(query, connection)
#     connection.close()
#     return response
# =============================================================================

@controller_blueprint.route('/master_agent_query', methods=['POST'])
def add_endpoint():
    data = request.get_json()
    
    # May need to modify prompt using context + prior prompts + prior api_name
    prompt = data['prompt']
    logger.debug(f"router is called with data: {data}")
    try:
        api_name = prompt2api(prompt, list_retriever)
        logger.debug(f"Retriever returns api_name as {api_name}")
    except Exception as e1:
        try:
            api_name = prompt2api(prompt, bm25_retriever)
            logger.debug(f"E1: Retriever returns api_name as {api_name}")
        except Exception as e2:
            try:
                api_name = prompt2api(prompt, retriever)
                logger.debug(f"E2: Retriever returns api_name as {api_name}")
            except Exception as e3:
                api_name = 'sales'
                logger.debug(f"E3: Retriever returns api_name as {api_name}")
                
    api_url = router.get(api_name)
    
    
    if not api_url:
        raise HTTPException(status_code=404, detail="API not found")
    
    logger.debug(f"Calling API... URL:{api_url}")
    response = requests.post(url = api_url,
                             json = data,
                             timeout = 30)
    
    #response['result']['detail'] = {'detail' : api_name}
    
    logger.debug(f"API call completed, status code:{response.status_code}")
    
    res = response.json()
        
# =============================================================================
#     with httpx.AsyncClient(timeout = 30) as client:
#         response = client.post(api_url, json=data)
#         response.raise_for_status()  # Raises an exception for HTTP errors
#         res = response.json()
# =============================================================================

    return res
                
@controller_blueprint.errorhandler(HTTPException) 
def http_exception_handler(exc):
    error_message = {"error_code": "router_error", "error_message" : "API not found"}
    content={"result": error_message}
    content['result']['detail'] = exc.detail
    return json.dumps(content), 200

@controller_blueprint.errorhandler(requests.exceptions.Timeout)
def timeout_exception_handler(exc):
    error_message = {"error_code": "router_error", "error_message" : "Time out"}
    content={"result": error_message}
    content['result']['detail'] = exc.detail
    return json.dumps(content), 200