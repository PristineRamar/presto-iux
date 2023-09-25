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
from bpr.bpr_tools import GetDataTool,PlotDataTool # PostProcessTool
from config.app_config import config

langchain.llm_cache = InMemoryCache()

api_key = config["open-ai"]["open_ai_key"]    
GPT_MODEL = "gpt-3.5-turbo-0613"

llm = ChatOpenAI(
    openai_api_key = api_key,
    model=GPT_MODEL,
    temperature=0
)

tools = [
    GetDataTool(),
    PlotDataTool()
    #GetDataTool(),
    #PostProcessTool(),
]

func_agent_sys_msg = '''You are an awesome assistant in retail. Only make function call to answer questions. You will try your best to figure out three pieces of information:

1. Products
2. Locations
3. Time Frames

Leave Product/Location/Time Frame fields blank if you are not sure do NOT make any assumptions.

Some Abbrevations you need to keep in mind:

W: Week, for example W3 means week 3.
P: Period, for example P3 means period 3.
Q: Quarter, for example Q2 means quarter 2.

And you have to answer the question in two step:  first call api to get data, then use the post process tool to get the final answer or use plotting tool to format the data for plotting. Answer exactly what is being asked, do NOT make any assumption about the metrics asked.

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
    
    message = "What Dairy promotions can I run to meet Q3 goals"
    message = "show HBC period 4 promos"
    
    print(message)
    #print(agent_executor.run(message))
    print(func_agent.run(message))
