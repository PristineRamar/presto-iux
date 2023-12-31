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
from generic.generic_llm_tools import GetDataTool, PostProcessTool, PlotDataTool
from config.app_config import config

import nltk

#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')

langchain.llm_cache = InMemoryCache()

api_key = config['open-ai']['open_ai_key']
GPT_MODEL = "gpt-3.5-turbo-0613"

llm = ChatOpenAI(
    openai_api_key = api_key,
    model=GPT_MODEL,
    temperature=0
)

summary_tools = [
    GetDataTool(),
    PostProcessTool(),
]

# Possible approach : ask the LLM to look for information in the current prompt, then check previous prompt if it can't determine
# something, otherwise leave blank.
summary_sys_msg = '''You are an awesome assistant in retail. Only make function call to answer questions.

Some Abbrevations you need to keep in mind:

W: Week, for example W3 means week 3.
P: Period, for example P3 means period 3.
Q: Quarter, for example Q2 means quarter 2.

And you have to answer the question in two steps: first call api to get data, then use the post process tool to get the final answer. 
'''


summary_agent_kwargs = {
    "system_message": SystemMessage(content= summary_sys_msg)
    }

summary_agent = initialize_agent(
    summary_tools,
    llm, 
    agent=AgentType.OPENAI_FUNCTIONS, 
    verbose=True, 
    agent_kwargs=summary_agent_kwargs,
    )


plot_tools = [
    GetDataTool(),
    PlotDataTool(),
]

# Possible approach : ask the LLM to look for information in the current prompt, then check previous prompt if it can't determine
# something, otherwise leave blank.
plot_sys_msg = '''You are an awesome assistant in retail. Only make function call to answer questions.

Some Abbrevations you need to keep in mind:

W: Week, for example W3 means week 3.
P: Period, for example P3 means period 3.
Q: Quarter, for example Q2 means quarter 2.

And you have to answer the question in two steps: first call api to get data, then use the plotting tool to format the data for generating plots or tables. Always return proper JSON data specified by the functions.
'''

plot_agent_kwargs = {
    "system_message": SystemMessage(content= plot_sys_msg)
    }

plot_agent = initialize_agent(
    plot_tools,
    llm, 
    agent=AgentType.OPENAI_FUNCTIONS, 
    verbose=True, 
    agent_kwargs=plot_agent_kwargs,
    )

if __name__ == '__main__':

    message = "Show me sales and movement for Upper Respiratory for Q2."
    summary_agent.run(message)

# =============================================================================
#     message = "Show me a table of sales and movement for Upper Respiratory for Q2."
#     plot_agent.run(message)
# 
#     message = "Show me a bar chart of sales and movement for Upper Respiratory for Q2."
#     plot_agent.run(message)
# =============================================================================