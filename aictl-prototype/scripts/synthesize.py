import os

import prompts
from langchain.llms import OpenAI

OPENAI_API_KEY = (
    open("../credentials/openai.key.txt").read().replace("\n", "").replace(" ", "")
)
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
llm = OpenAI(temperature=0)


def synthesize_conversational_prompts(queries, example):
    if not isinstance(queries, type([6, 9])):
        queries = queries.split("\n")
    samples = []
    for i, query in enumerate(queries):
        query = query.strip().replace("\n", "")
        text = example + "\nUser: " + query
        response = llm(text)
        samples.append(f"User: {query}\n{response}")
        print(f"User: {query}\n{response}")
        print("--------------------------------------")
    return samples


if __name__ == "__main__":
    samples = synthesize_conversational_prompts(
        prompts.QUERIES_PRICE_COMPARISON, prompts.PROMPT_PRICE_COMPARISON
    )
    with open("price-comparison.samples.txt", "w") as f:
        f.write("\n\n".join(samples))
