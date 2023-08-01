from langchain.llms import OpenAI
import os


def init_env_vars():
    OPENAI_API_KEY = (
        open("credentials/openai.key.txt").read().replace("\n", "").replace(" ", "")
    )
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


def make_llm(temperature=0.):
    init_env_vars()
    return OpenAI(temperature=temperature)
