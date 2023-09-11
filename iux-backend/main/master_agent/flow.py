# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 18:16:53 2023

@author: Dan
"""

import os
import re
import openai

from config.app_config import config
open_ai_key = config['open-ai']['open_ai_key']
os.environ["OPENAI_API_KEY"] = config['open-ai']['open_ai_key']

from llama_index.llms import OpenAI
from llama_index.embeddings import OpenAIEmbedding
from llama_index import (
    VectorStoreIndex, 
    ListIndex, 
    KeywordTableIndex,
    SimpleDirectoryReader,
    ServiceContext
)
from llama_index.node_parser import SimpleNodeParser
from llama_index.node_parser.extractors import MetadataExtractor, TitleExtractor, KeywordExtractor
from llama_index.indices.vector_store import VectorIndexRetriever
from llama_index.retrievers import BM25Retriever
from llama_index.indices.list import ListIndexLLMRetriever

def extract_tile(input_str):
    match = re.search(r'Title: (\w+)', input_str)
    if match:
        title = match.group(1)
    else:
        title = None
    return title

llm = OpenAI(model='gpt-4-0613', temperature=0, api_key = open_ai_key)
embed_model = OpenAIEmbedding(api_key = open_ai_key)

service_context = ServiceContext.from_defaults(llm =llm, embed_model = embed_model )
 
documents = SimpleDirectoryReader('./master_agent/route_descriptions').load_data()

titles = [extract_tile(s.text) for s in documents]

metadata_extractor = MetadataExtractor(
    extractors=[
        TitleExtractor(nodes=1),
        KeywordExtractor(keywords=5),
    ],
)

parser = SimpleNodeParser.from_defaults(
    chunk_size=4096,
    #metadata_extractor=metadata_extractor,
)

nodes = parser.get_nodes_from_documents(documents)

for node, title in zip(nodes, titles):
    node.metadata = {'title': title}

index = VectorStoreIndex(nodes, service_context=service_context)
list_index = ListIndex(nodes, service_context=service_context)

retriever = VectorIndexRetriever(index, similarity_top_k = 1)
bm25_retriever = BM25Retriever.from_defaults(index, similarity_top_k=1)
list_retriever = ListIndexLLMRetriever(list_index, similarity_top_k = 1)

if __name__ == '__main__':

    #message = "Give me a list of all items which had a cost change in Zone 620 during the last three weeks."
    message = "Show the trend for each store's Grocery sales during Q1"

    retrieved_nodes = retriever.retrieve(message)
    metadata = retrieved_nodes[0].node.metadata
    api_name = metadata['title']

    retrieved_nodes = bm25_retriever.retrieve(message)
    metadata = retrieved_nodes[0].node.metadata
    api_name = metadata['title']

    retrieved_nodes = list_retriever.retrieve(message)
    metadata = retrieved_nodes[0].node.metadata
    api_name = metadata['title']