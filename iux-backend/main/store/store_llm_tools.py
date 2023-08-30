import os
import io
import requests
import json
import pandas as pd
import time
import random
import string

from typing import Type
from typing import Optional, List
from pydantic import BaseModel, Field


import sys
sys.path.insert(0, '../schema')

from store.store_schema import get_data_by_api, plot_data #post_process_data 
from store.store_schema import APICallParameters, PlotDataParameters #PostProcessParameters

from langchain.tools import BaseTool, StructuredTool, Tool, tool

class StoreClusterTool(BaseTool):
    name="get_data_by_api"
    description = """
        Useful for extracting store name, competitor stores, no of groups, distance in miles, factors. 
        It will return the storee count, count of competing stores in miles and store clusters 
        Output will be a dictionary in the form of JSON.
        """
    args_schema: Type[BaseModel] = APICallParameters

    def _run(self, **kwargs):
        response = get_data_by_api(**kwargs)
        return response

    def _arun(self, **kwargs):
        raise NotImplementedError("get_data_by_api does not support async")

    
'''class PostProcessTool(BaseTool):
    name="post_process_data"
    description = """
        Used to print the output and processing time. 
        """
    args_schema: Type[BaseModel] = PostProcessParameters

    def _run(self, **kwargs):
        response = post_process_data(**kwargs)
        return response

    def _arun(self, **kwargs):
        raise NotImplementedError("post_process_data does not support async")'''
        
class PlotDataTool(BaseTool):
    name="plot_data"
    description = """
        Useful when formatting data for plotting or generating tables.
        """
    return_direct = True
    args_schema: Type[BaseModel] = PlotDataParameters
    
    def _run(self, **kwargs):
        response = plot_data(**kwargs)
        return response

    def _arun(self, **kwargs):
        raise NotImplementedError("post_process_data does not support async")

