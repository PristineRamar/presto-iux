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
    print('connection : ',connection_string)
    return connection_string

