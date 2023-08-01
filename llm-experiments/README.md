# LLM Experiments

Experiments with Large Language Models (LLMs) and langchain, a framework for developing LLM-based applications.

## Objective

The objective is to build an agent that can

- Interact with an end user in natural language
- Intent: Identify user's intent (eg: Get sales data for Q2)
- Entities: Identify and track entities like product name, location, etc, by asking follow-up questions
- Action: Perform a sequence of API calls
- Result: Respond to the user by populating a template with the results of the API calls

## Example

User:

```
"Show me sales and movement for Upper Respiratory for Q2."
```

Agent:

```
Observation: I need to call the Movement API for Upper Respiratory Quarter 2 sales and movement, and then display to user

Thought: I need the location, but user did not specify it

Action: Call Follow-Up Question API with {"type" = "location"}

Thought: User responded Zone 1000 Action: Call Movement API with {"product-name" = "Upper Respiratory", "quarter" = 2, "metrics" = ["sales", "movement"], "location-name" = "Zone 1000"}

Thought: I should use numerical format to diplay sales and movement

Action: Call Display API with {"type"="numeric", "data" = movement API response}
```

## Setup

```bash
# create a virtual environment
#  make sure you are using python 3.10.x
python3 -m virtualenv -p python3 env-llm
# activate virtual environment
source env-llm/bin/activate
# install requirements to experiment with API's (HuggingFace, OpenAI)
pip install -r requirements.api.txt
# **OR** install requirements to experiment with GPUs
pip install -r requirements.local.txt
# you are ready to go!
# you can run notebooks with:
# cd notebooks && jupyter notebook
```

## Agents

### Anu

Anu uses OpenAI embedding and OpenAI based LLM, to find prompts similar to the user's query and use them as context for answering the query. It is stateless. It neither tracks entities nor has the ability to hold multi-utterance conversations. It simply answers queries assuming that the user presents all the necessary information about the entities (product name, location, etc,) involved.

![](results/anu_v1.svg)

A critical issue in this agent is that the similarity search is the deciding factor in answering a query. The search simply compares sentence embeddings of query with contexts without abstracting away entity information. This leads to the problem of the similarity search yielding the wrong context due to similar entities being present in the query and the context. Wrong context will absolutely lead to wrong answers as the agent searches for an answer only within the context.


