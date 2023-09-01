"""
Created on Fri Jul 28 09:29:57 2023

@author: Priyanka
"""
import os
import sys
sys.path.insert(0, './')

os.chdir("E:/Users/Priyanka/FinalVersion-iux-agent-main/langchain")
from kvi.kvi_agent import func_agent as agent

#message = "Show top 10 KVIs for Oral Care use sales"
#message = "Show top 10 KVIs for Oral Care for summer"
#message = "Show top 10 KVIs for Oral Care for winter use sales"
#message = "Show top 10 KVIs for PAIN CAr."

#message = "Show the top 5 KVIs in Upper Respiratory by sales for summer." 
#message = "Show the top 10 KVIs in Upper Resp for east base in winter." 
#message = "Show the top 10 KVIs in Upper Resp Use visits, frequency and sales." 

#message = "Show top 10 KVIs for First Aid. "
#message = "Show top 10 KVIs for Oral Care. "

#message = "Find best 10 KVIs in upper resep " 
#message = "Show the top 10 KVIs in Upper Resp Use visits and sales." 
#message = "Find dairy kvis using household reach, frequency and sales"



#C & S
#message = "Show top 10 KVIs for for baby care for winter"
#message = "Show top 10 KVIs for for ICECREAM in C&S-Cortland"
#message = "Show the top 10 KVIs for ICECREAM in C&S-Cortland use visits, frequency and sales "
#message = "Show the top 10 KVIs in ICECREAM Use visits."
#message = "Show the top 10 KVIs in ICECREAM Use frequency."
#message = "Show the top 10 KVIs in ICECREAM for winter"
#message = "Show the top 10 KVIs in ICECREAM for C&S-Cortland in winter."


#message = "Show top 5 KVIs for for YOGURT "
#message = "Show top 10 KVIs for for YOGURT for winter in C&S-Peru"
#message = "Show the top 10 KVIs for YOGURT in C&S-Peru use visits "
#message = "Show the top 10 KVIs for YOGURT in C&S-Peru use visits, frequency and sales"

#message = "Show the top 10 KVIs in ICECREAM Use visits."
#message = "Show the top 10 KVIs in ICECREAM Use frequency."
#message = "Show the top 10 KVIs in ICECREAM for winter"
#message = "Show the top 10 KVIs in ICECREAM for C&S-Cortland in winter."

#message = "Show top 5 KVIs for for HAIR CARE"
#message = "Show top 10 KVIs for for HAIR CARE for winter"
#message = "Show top 10 KVIs for for  HAIR CARE in C&S-Peru"
#message = "Show top 10 KVIs for for  HAIR CARE in C&S-Peru for winter"
#message = "Show the top 10 KVIs for HAIR CARE in C&S-Peru use visits and frequency"

#message = "Show the top 10 KVIs in ICECREAM Use visits."
#message = "Show the top 10 KVIs in ICECREAM Use frequency and sales."
#message = "Show the top 10 KVIs in ICECREAM for C&S-Cortland in winter."

#Synthetic data
#message = "Find top 10 frozen meals kvis using visit for winter"
#message = "Find top 10 frozen meals key items using visit, frequency, and sales"
message = "Find top 10 upperresp kvis for BM11 for winter"
#message = "Find top 10 upperresp kvis for BM11 for summer"
#message = "Find best 10 kvi  frozen meals kvis using visit, frequency"
#message ="Find top 10 frozen groceri kvis for BM11 for summer using visit"

#message ="Find top 10 frozen brekfast and juice kvis for BM11 for summer using visit"





agent.run(message)

