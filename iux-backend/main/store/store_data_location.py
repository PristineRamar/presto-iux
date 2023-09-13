# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 12:56:47 2023

@author: Chavi
"""

#root_dir = 'E:\\Users\\Chavi\\code_from_git1\\presto-iux\\iux-backend\\main\\store\\'
import os

# Get the current working directory
current_dir = os.getcwd()

# Specify the subdirectory within the current working directory
subdirectory = 'store\\'

# Construct the full path to the desired directory
root_dir = os.path.join(current_dir, subdirectory)