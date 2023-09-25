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
from bpr.bpr_schema import get_data_by_api, plot_data #post_process_data 
from bpr.bpr_schema import APICallParameters, PostProcessParameters, PlotDataParameters

from langchain.tools import BaseTool, StructuredTool, Tool, tool



class GetDataTool(BaseTool):
    name="get_data_by_api"
    description = """
        Useful when getting better promotion recommendation data by product, location and time frame. 
        Output will be a dictionary in the form of JSON.
        """
    args_schema: Type[BaseModel] = APICallParameters

    def _run(self, **kwargs):
        response = get_data_by_api(**kwargs)
        return response

    def _arun(self, **kwargs):
        raise NotImplementedError("get_data_by_api does not support async")


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
        
'''
class GetDataTool(BaseTool):
    name="get_data_by_api"
    description = """
        Useful when getting retail data by product, location and time frame. 
        Output will be the name of the data file and the availabe columns in JSON.
        """
    args_schema: Type[BaseModel] = APICallParameters

    def _run(self, **kwargs):
        response = get_data_by_api(**kwargs)
        return response

    def _arun(self, **kwargs):
        raise NotImplementedError("get_data_by_api does not support async")

class PostProcessTool(BaseTool):
    name="post_process_data"
    description = """
        Useful when post processing the data retrieved.
        Output will be the either a numerical value or a list of strings in JSON.
        """
    args_schema: Type[BaseModel] = PostProcessParameters

    def _run(self, **kwargs):
        response = post_process_data(**kwargs)
        return response

    def _arun(self, **kwargs):
        raise NotImplementedError("post_process_data does not support async")
'''