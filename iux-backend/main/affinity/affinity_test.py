import sys
sys.path.insert(0, './')
from affinity.affinity_agent import func_agent as agent
#from iux_agent_16k import func_agent as agent
#from iux_custom_agent import agent_executor as agent

"ICE CREAM SINGLE DIP,ICE CREAM DOUBLE DIP,FLOWFLEX COVID19 AG TEST 1CT,COKE 20Z SINGLE,CKPOG L.FRANCES ORIG CRMLS.45Z,PEPSI 20Z SNGL BT,CRYSTAL GEYSER SPRWTR 1G,RED BULL 12Z SNGL CN,BW PURIFIED WATER 24/16.9Z,COKE DT SNGL BTL 20Z,AZ GREEN TEA 22Z PP,LED GLITTER GLOWMAN PP,SNICKERS SINGLE BAR 1.86Z,MT DEW 20Z SNGL BTL,BW DISTILLED WATR 1GALLON,M&M PEANUT 1.74Z,SPRITE 20Z SNGL BT,THRIFTY ROCKY ROAD 48Z,DR PEP 20Z SNGL BT,5 LB ICE ARTIC GLACIER,REESE KING SIZE 2.8Z,DORITOS NACHO CHEESE 9.25Z,REESE PNT BTR CUP 1.5Z,PLAN B ONE-STEP 1CT OTC,RED BULL 8.4Z SNGL CN,BINAXNOW COVID SELF-TEST,MNSTR ENRGY 16Z CN,AZ ARNOLD PALM 22Z PP,REESE PNT BTR EGG 1.2Z,TAKIS FUEGO 9.9Z,AZ MUCHO MANGO 22Z PP,THRIFTY COOKIES & CRM 48Z,PEPSI DT 20Z SNGL BT,SCOTT BATH TISSUE 4PK,COKE 16Z CN,LAYS REGULAR 8Z,COKE 2LITER,AZ LEMON TEA 22Z PP,AZ KIWI STRAW 22Z PP,THRIFTY MNT CHOC CHP 48Z,COKE ZERO PET SNGL 20Z,MODELO ESP 12Z 12PK BT,RED BULL SF 12Z SNGL CN,ESSENTIA WATER 1LTR,HRSHY KIT KAT 1.5Z,AZ FRUIT PUNCH 22Z PP,THRIFTY CHOC MLT KRNCH48Z,BW SPRING WATER SPRT 20Z,AF WATER 20Z,DORITOS NACHO 2.75Z,ESSENTIA 700ML SPORT CAP,SMARTWATER 1LT,TYL EX STR CAP 100CT,TAKIS FUEGO 4Z,BW PURIFIED WTR 16.9Z SNGL,THRIFTY PISTACHIO NUT 48Z,CD GNGR ALE 20Z PET,LAYS REGULAR 2.625Z,REESES PB PUMPKINS 1.2Z,M&M PNT TEAR-N-SHARE 3.27Z,GATORADE COOL BLUE 28Z,MNSTR ULTRA ZERO 16Z,COKE 12Z 12PK CN,PEPSI WLD CHRY 20Z SNGL BT,RA HYDROGEN PEROXIDE 16Z,CORONA 12Z 12PK LN BTL,SNICKERS KG SZ 3.29Z,PRNGLS ORIGINAL 2.36Z,GATORADE FRUIT PUNCH 28Z,WHOPPERS BOX 5Z,CHEEOTS FLAMIN HOT 3.25Z,THRIFTY RNBW SHRBT 48Z,PRNGLS SOUR CRM/ONION 2.5Z,JUNIOR MINTS 3.5Z,THRIFTY VANILLA 48Z,LINDOR TRUFFLES MILK 5.1Z,DORITOS COOL RANCH 9.25Z,THRIFTY BTTR PECAN 48Z,GLACIER ISLE 1L,MODELO ESP 12Z 12PK CAN,AZ SWEET TEA 22Z PP,THRIFTY BLK CHERRY 48Z,RA HYDROGEN PEROXIDE 32Z,CL ELECTROLYTE WATER 710ML,REESES PIECES THTR BX 4Z,SMARTWATER 700ML,GATORADE LEMON LIME 28Z,GATORADE FRST GLAC FRZ 28Z,COKE CHERRY SNGL BTTL 20Z,RPH RECOMMEND OTC,RA ALCOHOL ISP 91% LIQ 32Z,MIKE&IKE ORIG T/B 5Z,REESESTICKS KINGSIZE 3Z,SIMPLIFY PRFD WTR 16.9Z,DIGITAL PRINTS 4X6,FIJI WATER 0.5L,LUDENS WILD CHERRY 30CT,HRSHY MILK CHOC 1.55Z,THRIFTY FRNCH VAN 48Z,M&M PNT SHARING SIZE 10.7Z"
#message = "Give me a list of all items which had a cost change in Zone 620 during the last three weeks."
#message = "What people buy with BELG WEDGE PARMESAN?"
message = "What people buy with 1200988277?"
#message = message + ' in a table format'
#message = "What sells with SPRITE 20Z SNGL BT?"
#message = "What is the sales of OTC Internal in Q1?"
#message = "Give me a list of all items which had a cost change in Zone 620 during the last three weeks."
#message = "Which items from Eye/Ear Care are planned to be on BOGO in the coming week? Of these, how many will on page 1 of the ad?"
#message = "What percentage of Oral Care sales come from promoted ones during last week?"
#message = "What is the current cost of Item X?"
#message = "What is the current price of Item X?"
#message = "Give me a list of all items which had a cost change in Zone 620 during the last three weeks."
#message = "Which items from Eye/Ear Care are planned to be on BOGO in the coming week? Of these, how many will on page 1 of the ad?"
#message = "Tell me which items in OTC Internal had a cost change but no price change in the last period."

x = agent.run(message)