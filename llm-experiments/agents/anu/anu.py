import pandas as pd
import os

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI


DATA = "agents/anu/data.csv"
NSAMPLES = 3


def prepare_data(filepath=DATA):
    df = pd.read_csv(filepath)
    df = df[~df.Category.isna()].reset_index(drop=True)
    df = df.rename(columns={"Generated Prompts": "Query"})
    categories = df.Category.unique().tolist()
    return prepare_context_chunks(df, categories)


def construct_context(df, category, nsamples=NSAMPLES):
    category_df = df[df.Category == category]
    size = category_df.shape[0]
    nsamples = min(nsamples, size)
    df_n = category_df.sample(nsamples)
    context = f"{category}\n====\n\n"
    for _, row in df_n.iterrows():
        context += f"Q: {row.Query}\n{row.Response}\n\n"

    return context.strip()


def prepare_context_chunks(df, categories):
    text_chunks = []
    for category in categories:
        text_chunks.append(construct_context(df, category))
    return text_chunks


def init_env_vars():
    OPENAI_API_KEY = (
        open("credentials/openai.key.txt").read().replace("\n", "").replace(" ", "")
    )
    HF_KEY = (
        open("credentials/huggingface.key.txt")
        .read()
        .replace("\n", "")
        .replace(" ", "")
    )
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = HF_KEY


def init_agent(contexts):
    embeddings = OpenAIEmbeddings()
    docsearch = Chroma.from_texts(
        contexts,
        embeddings,
        metadatas=[{"source": str(i)} for i in range(len(contexts))],
    )
    chain = load_qa_chain(OpenAI(temperature=0), chain_type="stuff")
    return docsearch, chain


if __name__ == "__main__":
    # Parse csv file and create a list of text chunks (contexts)
    # Each context contains 3 or less examples for each type of query
    contexts = prepare_data()
    # Initialize API keys as environmental variables to access
    # [1] HuggingFace Inference endpoints (LLMs)
    # [2] HuggingFaceHub Embeddings
    # [3] OpenAI embeddings
    # [4] OpenAI models (LLMs)
    init_env_vars()
    # Setup Context similarity search and LLM
    docsearch, chain = init_agent(contexts)

    def interact(q):
        context = docsearch.similarity_search(q, k=1)
        print("\033[91m" + context[0].page_content.split("\n")[0].strip())
        return chain.run(input_documents=context, question=q)

    while True:
        q = input("\033[92m" + "Q: ")
        cmd = q.replace(" ", "").replace("\n", "")
        if cmd == "q" or cmd == "Q" or cmd == "exit" or cmd == "quit":
            break
        a = interact(q)
        print("\033[93m" + a, "\n")
