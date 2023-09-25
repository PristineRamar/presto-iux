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
from generic.generic_schema import (get_data_by_api, post_process_data, plot_data,
                                                     APICallParameters, PostProcessParameters,
                                                     PlotDataParameters)

from langchain.tools import BaseTool, StructuredTool, Tool, tool
from app_logger.logger import logger

class GetDataTool(BaseTool):
    name="get_data_by_api"
    description = """
        Useful when getting retail data by product, location and time frame. 
        Output will be the name of the data file and the availabe columns in JSON.
        """
    args_schema: Type[BaseModel] = APICallParameters
    #return_direct = True
    def _run(self, **kwargs):
        response = get_data_by_api(**kwargs)
        logger.debug(f"response in get_data_by_api: {response}")
        return response

    def _arun(self, **kwargs):
        raise NotImplementedError("get_data_by_api does not support async")

class PostProcessTool(BaseTool):
    name="post_process_data"
    description = """
        Useful when post processing the data retrieved.
        Output will be the either a numerical value or a list of strings in JSON.
        """
    return_direct = True
    args_schema: Type[BaseModel] = PostProcessParameters

    def _run(self, **kwargs):
        logger.debug("post_process_data starts...")
        logger.debug(f"kwargs {kwargs}")
        response = post_process_data(**kwargs)
        logger.debug(f"response in post: {response}")
        return response

    def _arun(self, **kwargs):
        raise NotImplementedError("post_process_data does not support async")

class PlotDataTool(BaseTool):
    name="plot_or_table_data"
    description = """
        Useful when formatting data for plotting or generating tables.
        """
    return_direct = True
    args_schema: Type[BaseModel] = PlotDataParameters

    def _run(self, **kwargs):
        logger.debug("plot_data starts...")
        response = plot_data(**kwargs)
        logger.debug(f"response in plot_data: {response}")
        return response

    def _arun(self, **kwargs):
        raise NotImplementedError("plot_or_table_data does not support async")
