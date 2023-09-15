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

from recommendation.recommendation_schema import get_data
from recommendation.recommendation_schema import APICallParameters

from langchain.tools import BaseTool, StructuredTool, Tool, tool


class DataTool(BaseTool):
    name="get_data"
    description = """
        Useful when getting productId ,productLevelId,location id and location level id . 
        Output will be the availabe columns in JSON required for calling the recommendation API.
        """
    return_direct = True
    args_schema: Type[BaseModel] = APICallParameters

    
    def _run(self, **kwargs):
        print('values of kwargs:  ',kwargs)
        response = get_data(**kwargs)
        return response

    def _arun(self, **kwargs):
        raise NotImplementedError("get_data_by_api does not support async")
