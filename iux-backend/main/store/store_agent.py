import os
import sys
import langchain
from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from langchain import LLMMathChain
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain.cache import InMemoryCache
sys.path.insert(0, './')

from store.store_llm_tools import StoreClusterTool, PlotDataTool#PostProcessTool #GetDataTool 


langchain.llm_cache = InMemoryCache()
api_key= "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"
#api_key = os.environ.get("OPEN_AI_API")
#GPT_MODEL = "gpt-3.5-turbo-0613"
GPT_MODEL = "gpt-4-0613"

llm = ChatOpenAI(
    openai_api_key = api_key,
    model=GPT_MODEL,
    temperature=0
)

tools = [
    StoreClusterTool(),
    PlotDataTool()
   # GetDataTool(),
   #PostProcessTool()
]
func_agent_sys_msg = '''You are an awesome assistant in retail. Only make function call to answer questions. You will try your best to figure out eight pieces of information:

1. API to use
2. Store Name
3. Competitor Store Names
4. Distance in miles
5. No of groups
6. Factors
7. State
8. nostore
9. Geography
10. City
11. min_store
12. max_store


Map the correct Store Name in case its abbreviation is given.
DG : Dollar General, GU : Grand Union, DT : Dollar Tree

Leave Competitor Store Name/Distance in miles/no of groups/factors/City/State fields blank if you are not sure. 
You have to identify one correct API  based on factors given and intent of user, for each scenario, and present result as it is.
Do not use PlotDataTool for any task other than grouping or clustering.
Answer exactly what is being asked, DO NOT make any assumption about the metrics asked or add any additional information.
Report exactly what the tools returns. DO NOT mention API to use in summary
'''

agent_kwargs = {
    "system_message": SystemMessage(content= func_agent_sys_msg)
    }

func_agent = initialize_agent(
    tools,
    llm, 
    agent=AgentType.OPENAI_FUNCTIONS, 
    verbose=True, 
    agent_kwargs=agent_kwargs,
    )

#res = func_agent.run(prompt)
#print(res)
llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=True)
agent_tools = [
    Tool.from_function(
        func=func_agent.run,
        name="Retrieve Data",
        description="useful for when you need to retrieve and summarize data"
    ),
    Tool(
        name="Calculator",
        func=llm_math_chain.run,
        description="useful for when you need to answer questions about math"
    ),
    ]

agent_executor = initialize_agent(
    agent_tools,
    llm, 
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True, 
    #agent_kwargs=agent_kwargs,
    )

#from langchain.experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner
#planner = load_chat_planner(llm)
#executor = load_agent_executor(llm, tools, verbose=True)
#planning_agent = PlanAndExecute(planner=planner, executor=executor, verbose=True)
#res = planning_agent.run(prompt)

if __name__ == '__main__':
    '''message = "Show me sales and movement for Upper Respiratory for Q2."
    message = "What percentage of grocery sales come from promoted ones?"
    message = "Show me sales and margin of Oral Care."
    message = "What is the current cost of Item X?"
    message = "What is the current price of Item X?"
    message = "Give me a list of all items which had a cost change in Zone 620 during the last three weeks."'''
    
    #message = "Which items from Eye/Ear Care are planned to be on BOGO in the coming week? Of these, how many will on page 1 of the ad?"
    #message = "Tell me which items in OTC Internal had a cost change but no price change in the last period." 
    
    message = "Find all 168 Market stores in US" #walmart, cvs, walgreens
    #message="Find 5 groups of Gaint Egl  stores on the basis of rural, suburban,state and distance from Aldi"
   #message="Find 10 groups of Aldi stores on the basis of rural, suburban,state and distance from walmart"
   #message="Find 5 groups of cvs stores on the basis of rural, suburban,state and distance from walgrin and dollar tree"
   # message= "find all stores of aldi withing 3 miles of giant eagle"
    #message= "find all stores of grand union withing 1,3 and 5 miles of price chopper"
   # message="create 3 groups of aldi based on state, rural, and distance from giant eagle"
   # message="create 3 groups of grand union based on urban, state and 3 miles distance from Price Chopper"
    #message ="how many cvs stores are there within 5 miles of cortland store"


    print(message)
    print(agent_executor.run(message))
    print(func_agent.run(message))
