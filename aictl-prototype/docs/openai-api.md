To use the OpenAI API via LangChain, you can follow these steps to build applications:

1. **Get Access to OpenAI API**: Sign up for OpenAI API access and obtain an API key from OpenAI.

2. **Install LangChain**: Install the LangChain library, which is a Python library developed by OpenAI that provides a high-level interface to the OpenAI API.

```bash
pip install langchain
```

3. **Import the necessary modules**: In your Python script, import the LangChain module and authenticate using your OpenAI API key.

```python
import langchain

# Set your OpenAI API key
langchain.set_api_key('YOUR_API_KEY')
```

4. **Make API calls**: Use the LangChain library to make API calls to OpenAI and interact with the models. The following example demonstrates how to use the `langchain.Completion` class to generate text:

```python
# Initialize a completion instance
completion = langchain.Completion()

# Set the model configuration
completion.set_model("text-davinci-003")

# Set the prompt text
prompt = "Once upon a time"

# Generate text
response = completion.complete(prompt)

# Get the generated text from the response
generated_text = response['choices'][0]['text']

# Print the generated text
print(generated_text)
```

This is a simple example that generates text using the "text-davinci-003" model. You can explore different models and their capabilities in the OpenAI documentation.

Remember to handle exceptions, manage API rate limits, and follow OpenAI's usage guidelines when integrating the OpenAI API into your applications.

Please note that the example provided here is a basic illustration, and you may need to adapt it based on your specific application requirements and desired functionality. The LangChain library offers additional functionalities like language translation and summarization, which you can explore further in the documentation.

For detailed information on how to use the OpenAI API via LangChain, including examples and documentation, refer to the official LangChain repository on GitHub: https://github.com/openai/langchain
