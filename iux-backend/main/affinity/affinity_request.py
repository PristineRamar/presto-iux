# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 11:33:39 2023

@author: Ashutosh
"""

import requests
import json

input_json = {'prompt':'What people buy with PANCAKE SYRUP?'}

response = requests.post('http://127.0.0.1:9506/getAffinity', json = input_json)

response = response.json()

print(response)