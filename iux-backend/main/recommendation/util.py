# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 01:13:37 2023

@author: Karishma
"""

import cx_Oracle
from flask import Flask, jsonify,request
import difflib 
import re
from config.app_config import config


def connectionString():
    db_username = config['database']['username']
    db_password = config['database']['password']
    db_name = config['database']['dbname']
    connection_string = f"{db_username}/{db_password}@{db_name}"

    return connection_string


def getDetailsUsingFuzzySearch(df, name, n):

        exact_match = df.get(name.upper)

        if exact_match is None:
                sim = difflib.get_close_matches(
                    re.sub(r'[^a-zA-Z0-9]', ' ', name).upper(), list(df.keys()), n=n)
              
                if sim:
                    
                    closest_match = df.get(sim[0])
                   ## print('closest_match',closest_match)
                    if closest_match is not None:
                            return sim[0] 
                    else :
                        return None
                else:
                    return None
      
        return name
    
    
