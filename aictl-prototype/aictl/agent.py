import logging
import os
from datetime import datetime
from random import shuffle

import lookup.apidesc as apidesc
import pandas as pd
import prompts
from langchain.chains.question_answering import load_qa_chain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma

DATA = "data/samples.csv"
NSAMPLES = 5

# Configure the logging
logging.basicConfig(
    filename="chat.log",
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def log_chat(messages):
    for msg in messages:
        logging.info(f"{msg['role']}: {msg['content'].strip()}")


def prepare_data(filepath=DATA, df=None):
    """
    Prepares the data for context chunks.

    This function prepares the data for context chunks by reading a CSV file located at the specified filepath or using a DataFrame
    if provided. The DataFrame is processed to remove rows with missing category values and rename a specific column.
    The unique categories are extracted and returned along with the prepared context chunks.

    Args:
        filepath (str, optional): The path to the CSV file. Defaults to "data/samples.csv".
        df (pandas.DataFrame, optional): The DataFrame containing the data. Defaults to None.

    Returns:
        tuple: A tuple containing the prepared context chunks and unique categories.

    Example:
        prepare_data(filepath="data/samples.csv") prepares the data from the specified CSV file and returns the context chunks
        and unique categories.
    """
    if df is None:
        df = pd.read_csv(filepath)
    df = df[~df.Category.isna()].reset_index(drop=True)
    df = df.rename(columns={"Generated Prompts": "Query"})
    categories = df.Category.unique().tolist()
    return prepare_context_chunks(df, categories), categories


def create_context_chunks_from_dataframe(df, nsamples=3):
    """
    Creates context chunks from a DataFrame.

    This function creates context chunks from a DataFrame by iterating over unique categories. For each category, a context chunk is
    constructed by sampling a specified number of samples and concatenating the role, utterance, and query/response pairs.
    The context chunks and unique categories are returned.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        nsamples (int, optional): The maximum number of samples to include. Defaults to 3.

    Returns:
        tuple: A tuple containing the created context chunks and unique categories.

    Example:
        create_context_chunks_from_dataframe(df, nsamples=3) creates context chunks from the provided DataFrame, ensuring that
        each context chunk contains up to 3 samples per category.
    """
    contexts = []
    categories = df.Category.unique().tolist()
    for category in categories:
        category_context = [category, "----------------", ""]
        catdf = df[df.Category == category]
        sids = catdf.SynthId.unique().tolist()
        shuffle(sids)
        nsamples = min(nsamples, len(sids))
        for sid in sids[:nsamples]:
            udf = catdf[catdf.SynthId == sid].sort_values("UtteranceIndex")
            for i, row in udf.iterrows():
                category_context.append(f"{row.Role}: {row.Utterance}")
            category_context.append("")

        contexts.append("\n".join(category_context))

    return contexts, categories


def construct_context(df, category, nsamples=NSAMPLES):
    """
    Constructs a context for a specific category.

    This function constructs a context for a specific category by selecting a specified number of samples randomly from the DataFrame
    for that category. The category, query, and response pairs are concatenated into a single context string.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        category (str): The category for which to construct the context.
        nsamples (int, optional): The maximum number of samples to include. Defaults to 5.

    Returns:
        str: The constructed context.

    Example:
        construct_context(df, category) constructs a context for the specified category by selecting random samples from the DataFrame
        and concatenating the query and response pairs.
    """
    category_df = df[df.Category == category]
    size = category_df.shape[0]
    nsamples = min(nsamples, size)
    df_n = category_df.sample(nsamples)
    context = f"{category}\n====\n\n"
    for _, row in df_n.iterrows():
        context += f"Q: {row.Query}\n{row.Response}\n\n"

    return context.strip()


def prepare_context_chunks(df, categories):
    """
    Prepares context chunks for each category.

    This function prepares context chunks for each category by iterating over the unique categories and constructing a context for
    each category using the construct_context function. The prepared context chunks are returned.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        categories (list): The unique categories.

    Returns:
        list: The prepared context chunks.

    Example:
        prepare_context_chunks(df, categories) prepares context chunks for each category in the provided DataFrame.
    """
    text_chunks = []
    for category in categories:
        text_chunks.append(construct_context(df, category))
    return text_chunks


def init_env_vars():
    """
    Initializes environment variables.

    This function initializes environment variables by reading the OpenAI API key from a file and setting it as an environmental
    variable.

    Example:
        init_env_vars() initializes the environment variables by reading the OpenAI API key from a file and setting it as an
        environmental variable.
    """
    OPENAI_API_KEY = (
        open("credentials/openai.key.txt").read().replace("\n", "").replace(" ", "")
    )
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


def init_agent(contexts, temperature=0.0, return_chain=False):
    """
    Initializes the context similarity search and LLM.

    This function initializes the context similarity search and the Language Learning Model (LLM) by creating embeddings,
    initializing the vector store, and loading the question-answering chain.
    The initialized context similarity search and chain are returned.

    Args:
        contexts (list): The prepared context chunks.

    Returns:
        tuple: A tuple containing the initialized context similarity search and the loaded question-answering chain.

    Example:
        init_agent(contexts) initializes the context similarity search and LLM using the provided context chunks.
    """
    embeddings = OpenAIEmbeddings()
    docsearch = Chroma.from_texts(
        contexts,
        embeddings,
        metadatas=[{"source": str(i)} for i in range(len(contexts))],
    )
    llm = OpenAI(temperature=temperature)
    if return_chain:
        docsearch, load_qa_chain(llm, chain_type="stuff")
    return docsearch, llm


def create_api_callable(contexts=None, categories=None):
    """
    Creates an API callable function for interacting with the model.

    This function creates an API callable function for interacting with the model. If the contexts and categories are not provided,
    the data is prepared using the prepare_data function. The environment variables are initialized using the init_env_vars function.
    The context similarity search and LLM are initialized using the init_agent function.
    The model creation timestamp is recorded and the interact function is defined.

    Args:
        contexts (list, optional): The prepared context chunks. Defaults to None.
        categories (list, optional): The unique categories. Defaults to None.

    Returns:
        function: An API callable function for interacting with the model.

    Example:
        create_api_callable() creates an API callable function for interacting with the model using the prepared context chunks
        and unique categories.
    """
    # Parse csv file and create a list of text chunks (contexts)
    # Each context contains 3 or less examples for each type of query
    if contexts is None and categories is None:
        contexts, categories = prepare_data()
    # Initialize API keys as environmental variables to access
    init_env_vars()
    # Setup Context similarity search and LLM
    docsearch, chain = init_agent(contexts)
    model_creation_ts = datetime.now().strftime("%d-%B-%Y %H:%M:%S")

    def interact(q):
        print("Model created at", model_creation_ts)
        context = docsearch.similarity_search(q, k=1)
        return chain.run(input_documents=context, question=q)

    return interact


def update_model(rows):
    """
    Updates the model based on new data.

    This function updates the model based on new data by converting the provided rows into a DataFrame, creating new context chunks,
    and creating an API callable function for interacting with the updated model using the create_api_callable function.
    The updated API callable function is returned.

    Args:
        rows (list): The rows of data to update the model.

    Returns:
        function: An updated API callable function for interacting with the model.

    Example:
        update_model(rows) updates the model based on the provided rows of data and returns an updated API callable function.
    """
    df = pd.DataFrame(rows[1:], columns=rows[0])
    contexts, categories = create_context_chunks_from_dataframe(df)
    return create_api_callable(contexts, categories)


def read_api_desc_locally():
    df = pd.read_csv("../data/api_desc.csv")
    records = df.to_dict("tight")["data"]
    columns = df.columns.tolist()
    return [columns] + records


def create_chatbot_using_api_description(rows=None):
    # get data locally if necessary
    rows = read_api_desc_locally()
    # initialize api key
    init_env_vars()
    contexts = apidesc.prepare_context(rows)
    docsearch, llm = init_agent(contexts)
    model_creation_ts = datetime.now().strftime("%d-%B-%Y %H:%M:%S")

    def sanitize_response(resp):
        # if "(" in resp and ")" in resp and "=" in resp:
        return resp.replace("AI:", "").strip()

    def interact(q, history):
        print("Model created at", model_creation_ts)

        context = docsearch.similarity_search(q, k=2)
        prompt = prompts.build_api_description_prompt(context, q)
        prompt += "\n"
        for item in history:
            role, content = item["role"], item["content"]
            if f"{role}:" in item["content"]:
                prompt += f"\n{content}"
            else:
                prompt += f"\n{role}: {content}"
        prompt += f"\nUser: {q}"
        response = llm(prompt)
        interaction = [
            {"role": "User", "content": q},
            {"role": "AI", "content": response},
        ]
        log_chat(interaction)
        return sanitize_response(response), history + interaction

    return interact
