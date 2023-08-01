API_DESCRIPTION_INSTRUCTION = """
You are an AI that will answer the user's query by returning python code that uses the api mentioned above. If one or more arguments are missing do not respond with python code. Instead ask the user for missing arguments.
"""


def build_api_description_prompt(context, query):
    return f"""{context}\n
    {API_DESCRIPTION_INSTRUCTION}\n
    {query}
    """
