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
from recommendation.recommendation_llm_tools import DataTool
from config.app_config import config


langchain.llm_cache = InMemoryCache()
api_key = config["open-ai"]["open_ai_key"] 
GPT_MODEL = "gpt-3.5-turbo-0613"   
#GPT_MODEL = config["agent"]["llm-model"]

llm = ChatOpenAI(
    openai_api_key = api_key,
    model=GPT_MODEL,
    temperature=0
)

tools = [
    DataTool(),
]

func_agent_sys_msg = '''You are an awesome assistant in retail. Only make function call to answer questions. You will try your best to figure out below piece of information:

1. API to use

Leave Product/Location/fields blank if you are not sure.

Some Abbrevations you need to keep in mind:
    run: Recommend
    trigger: Recommend
    run online :Recommend
    review :complete review
    approve: aprove for export

And you have to answer the question in two steps: first call get_data function which will get the location and product details, 
then call the api  use the post process tool to get the final answer which will provide the status weather the recommendation has been added to queue or there was any error. Answer exactly what is being asked, do NOT make any assumption about the metrics asked. Report exactly what the tools returns.
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
    message = "Show me sales and movement for Upper Respiratory for Q2."
    message = "What percentage of grocery sales come from promoted ones?"
    message = "Show me sales and margin of Oral Care."
    message = "What is the current cost of Item X?"
    message = "What is the current price of Item X?"
    message = "Give me a list of all items which had a cost change in Zone 620 during the last three weeks."

    #message = "Which items from Eye/Ear Care are planned to be on BOGO in the coming week? Of these, how many will on page 1 of the ad?"
    #message = "Tell me which items in OTC Internal had a cost change but no price change in the last period."
    print(message)
    #print(agent_executor.run(message))
    print(func_agent.run(message))