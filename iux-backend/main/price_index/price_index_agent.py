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
from price_index.price_index_llm_tools import GetDataTool, PostProcessTool, PlotDataTool

langchain.llm_cache = InMemoryCache()

api_key = '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'
GPT_MODEL = "gpt-3.5-turbo-0613"
#GPT_MODEL = "gpt-4-0613"

llm = ChatOpenAI(
    openai_api_key = api_key,
    model=GPT_MODEL,
    temperature=0,
    
)

tools = [
    GetDataTool(),
    PostProcessTool(),
    PlotDataTool(),
]

func_agent_sys_msg = '''You are an awesome assistant in retail. Only make function call to answer questions. You will try your best to figure out 8 pieces of information:

1. API to use
2. Products
3. Locations
4. Time Frames
5. child product level 
6. aggregation flags 

7. price index type
8. weighted by parameters 


Leave Product/Location/Time Frame/aggregation flags if flags are 'Y'/child product level/price index type/weighted by/
fields blank if you are not sure.

Some Abbrevations you need to keep in mind:

W: Week, for example W3 means week 3.
P: Period, for example P3 means period 3.
Q: Quarter, for example Q2 means quarter 2.
PI: Price index

And you have to answer the question in two steps: first call api to get data, then use the post process tool to get the final answer or use plotting tool to format the data for plotting. Answer exactly what is being asked, do NOT make any assumption about the metrics asked. Report exactly what the tools returns. And if asked about ratio or percentage, you have to call the same API twice with different flags.
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
    message = "Show me price index data  for Grocery for last quarter."
    
    #message = "Which items from Eye/Ear Care are planned to be on BOGO in the coming week? Of these, how many will on page 1 of the ad?"
    #message = "Tell me which items in OTC Internal had a cost change but no price change in the last period."
    print(message)
    print(agent_executor.run(message))
    print(func_agent.run(message))
