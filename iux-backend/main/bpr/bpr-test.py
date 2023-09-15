"""
Created on Fri Jul 28 09:29:57 2023

@author: Priyanka
"""
import os
import sys
sys.path.insert(0, './')

#os.chdir("E:/Users/Priyanka/GIT Project/FinalVersion-iux-agent-main")
from bpr.bpr_agent import func_agent as agent

message = "What Dairy promotions can I run to meet Q3 goals"
#message = "show HBC period 4 promos"


agent.run(message)

