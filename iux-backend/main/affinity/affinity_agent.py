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
from affinity.affinity_llm_tools import GetDataTool, PostProcessTool,PlotDataTool
from config.app_config import config

langchain.llm_cache = InMemoryCache()

api_key = config["open-ai"]["open_ai_key"]    
GPT_MODEL = config["agent"]["llm-model"]


llm = ChatOpenAI(
    openai_api_key = api_key,
    model=GPT_MODEL,
    temperature=0
)

tools = [
    GetDataTool(),
    #PostProcessTool(),
    PlotDataTool()
]

func_agent_sys_msg = '''You are an awesome assistant in retail. Only make function call to answer questions. You will try your best to figure out four pieces of information:

1. API to use
2. Products
3. Locations
4. Time Frames

Leave Product/Location/Time Frame fields blank if you are not sure.

Also keep in mind, if question asks for association between products,call affinity API
For example if questions asks which products are sold or bought together call affinity API

Use Plot Data Tool if table format asked otherwise use post process tool.
Keep the name of base item in final answer.

And you have to answer the question in four steps: first call api to get data,then state the name of base item,then use plot data tool for table format  and attach it to final answer.


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

# if __name__ == '__main__':
#     message = "Show me sales and movement for Upper Respiratory for Q2."
#     message = "What percentage of grocery sales come from promoted ones?"
#     message = "Show me sales and margin of Oral Care."
#     message = "What is the current cost of Item X?"
#     message = "What is the current price of Item X?"
#     message = "Give me a list of all items which had a cost change in Zone 620 during the last three weeks."

#     #message = "Which items from Eye/Ear Care are planned to be on BOGO in the coming week? Of these, how many will on page 1 of the ad?"
#     #message = "Tell me which items in OTC Internal had a cost change but no price change in the last period."
#     print(message)
#     #print(agent_executor.run(message))
#     print(func_agent.run(mess
                         
                         
