# iux-agent
This is the IUX controller implemented with OPEN AI API

# To run the agent locally:

```bash
python iux-test.py
```

# To run the app as a REST API:

```bash
python iux-app.py
```

# To run the streamlit APP:

```bash
streamlit run iux-st-app.py --server.port 8001
```

# How to develop new agents ?

1. The first step is to build your REST services that LLMs will call. Here is an example API to get price information:

```python
        @app.route('/price', methods = ['POST'])
         
        def price():
             
            input_json = request.get_json()
            output_json = dict()
             
            try:
                response = price_api(product_name = input_json['product-name'] if 'product-name' in input_json else None,
                                     product_id = input_json['product-id'] if 'product-id' in input_json else None,
                                     product_level = input_json['product-level'] if 'product-level' in input_json else None,
                                     item_list = input_json['item-list'] if 'item-list' in input_json else None,
                                     active = input_json['active'] if 'active' in input_json else 'Y',
                                     location_name = input_json['location-name'] if 'location-name' in input_json else None,
                                     location_id = input_json['location-id'] if 'location-id' in input_json else None,
                                     location_level = input_json['location-level'] if 'location-level' in input_json else None,
                                     cal_year = input_json['cal-year'] if 'cal-year' in input_json else None,
                                     quarter = input_json['quarter'] if 'quarter' in input_json else None,
                                     period = input_json['period'] if 'period' in input_json else None,
                                     week = input_json['week'] if 'week' in input_json else None,
                                     day = input_json['day'] if 'day' in input_json else None,
                                     start_date = input_json['start-date'] if 'start-date' in input_json else None,
                                     end_date = input_json['end-date'] if 'end-date' in input_json else None,
                                     calendar_id = input_json['calendar-id'] if 'calendar-id' in input_json else None,
                                     cal_type = input_json['cal-type'] if 'cal-type' in input_json else None,
                                     user_id = input_json['user-id'])
                
                output_json['timeframe'] = response[3]
                output_json['locations'] = response[2]
                output_json['products'] = response[1]
                output_json['data'] = json.loads(response[0].to_json(orient = 'records').replace('\\', ''))          
                
            except:
                output_json['error-message'] = 'Could not process request.'
            return json.dumps(output_json)
```

Follow the examples in the file `data-api/data_api.py` file.

2. Write a python function to call the API you've created:

Here is an example:

```python
        def get_data_by_api(**kwargs):

            print(kwargs)

            api_name = kwargs.pop('api_name')
            print(api_name)

            if 'url' in kwargs:
                url = kwargs.pop('url')
            else:
                #url = 'http://127.0.0.1:5001/'
                url = 'http://65.61.166.184:5001/'

            if 'user-id' in kwargs:
                user_id = kwargs.pop('user-id')
            else:
                user_id  = 'ejack'

            endpoint = url + api_name
            #converted_dict = {key.replace('-', '_'): value for key, value in kwargs.items()}
            converted_dict = {key.replace('_', '-'): value for key, value in kwargs.items()}

            headers = {'Content-Type': 'application/json'}
            #args =  {'user-id': '111'} 
            args =  converted_dict | {'user-id': user_id} 
            print(args)
            response = requests.post(endpoint, headers = headers, json = args)

            if response.status_code == 200:
                data = response.json()
                timestamp = time.strftime('%Y%m%d%H%M%S')
                random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
                file_name = f'response_{timestamp}_{random_string}.json'

                with open(file_name, 'w') as file:
                    json.dump(data, file)
                    #print(f'JSON data saved to {file_name}')
            else:
                print(f'Request failed with status code {response.status_code}')

            df = pd.DataFrame(data['data'])
            cols = df.columns.tolist()

            res = {}
            res['data_file'] = file_name
            res['columns'] = cols

            meta_keys = ['timeframe', 'locations', 'products']
            meta_data = {key: data[key] for key in meta_keys if key in data}
            with open('meta-data.json', 'w') as file:
                json.dump(meta_data, file)

            return json.dumps(res)
```

In this example, we need to specify the input and the output formats, both in JSON.
The input format is VERY IMPORTANT and STRICT, and it's actually specified by
a Pydantic class.

```python
        class APICallParameters(BaseModel):
            """Inputs for get_data_by_api"""
            api_name: str = Field(
                ...,
                description="APIs to call: 1. Movement API: it returns the weekly movement, sales, and margin data; 2. Price API: it returns the weekly regular prices; 3. Cost API: it returns the weekly list costs for all items; 4. Promotion API: it returns the weekly promotion types and sale prices.",
                enum=["movement", "price", "cost", "promotion"]
            )
            product_name: Optional[List[str]] = Field(
                None,
                description="Used to specify which product group the user wants data pertaining to. For example, 'Upper Respiratory', 'OTC internal',  or 'grocery' would be valid ways of using this argument."
            )
            #item_list: Optional[List[str]] = Field(
                #None,
                #description="A list of items the user wants data pertaining to."
            #)
            location_name: Optional[List[str]] = Field(
                None,
                description="Used to specify the location the user wants data pertaining to. For example, 'Zone 620' or 'online stores' would be valid ways of using this argument."
            )
            week: Optional[List[str]] = Field(
                None,
                description="Can be used to specify specific weeks in the retail calendar, e.g., ['7'] or ['46', '47', '48']. Alternatively, the user can specify certain weeks using key phrases such as 'current', 'last 4', or 'next 6'."
            )
            period: Optional[List[str]] = Field(
                None,
                description="Can be used to specify specific periods in the retail calendar, e.g., ['4'] or  ['5', '6']. Alternatively, the user can specify certain periods using key phrases such as 'current', 'last 1', or 'next 2'."
            )
            quarter: Optional[List[str]] = Field(
                None,
                description="Can be used to specify specific quarters in the retail calendar, e.g., ['1'] or  ['2', '3']. Alternatively, the user can specify certain quarters using key phrases such as 'current', 'last 1', or 'next 2'."
            )
            cal_year: Optional[List[str]] = Field(
                None,
                #alias="cal-year",
                description="Can be used to specify specific years in the retail calendar, e.g., ['2021'] or  ['2022', '2023']. Alternatively, the user can specify certain years using key phrases such as 'current', 'last 1', or 'next 2'."
            )
            start_date: Optional[str] = Field(
                None,
                #alias="start-date",
                description="Can be used to specify that the user wants information from a certain date onwards, e.g., 'May 12, 2021'."
            )
            end_date: Optional[str] = Field(
                None,
                #alias="end-date",
                description="Same as start-date"
            )
            change: Optional[str] = Field(
                None,
                description= "A flag to indicate if the query is about change. This flag only applis to cost and price APIs.",
                enum=["All", "Yes", "No"]
            )
            promoted: Optional[str] = Field(
                None,
                description="A flag that only applies to Movement API.",
                enum=["Yes", "No", "All"]
            )
            promo_type: Optional[str] = Field(
                None,
                description="A flag that only applies to Promotion API.",
                enum=["Stardard", "BOGO"]
            )
            page_no: Optional[int] = Field(
                None,
                description="A flag that only applies to Promotion API: the page no of the promotion",
            )
            block_no: Optional[int] = Field(
                None,
                description="A flag that only applies to Promotion API: the block no of the promotion",
            )
```

This is the format we are asking LLMs to use when repsonding our queries. You will see how this instruction is given
to the LLMs when we construct the tools later on.

The output format is somehow arbitary (still in JSON format though): we just need to tell the LLMs the actual results
of calling this function.

3. Tool construction.

Here we customize the Langchain 'BaseTool' class to make our own tools:

```python
        class GetDataTool(BaseTool):
            name="get_data_by_api"
            description = """
                Useful when getting retail data by product, location and time frame. 
                Output will be the name of the data file and the availabe columns in JSON.
                """
            args_schema: Type[BaseModel] = APICallParameters

            def _run(self, **kwargs):
                response = get_data_by_api(**kwargs)
                return response

            def _arun(self, **kwargs):
                raise NotImplementedError("get_data_by_api does not support async")
```

Please note we are passing `APICallParameters` as the schema when constructing the tool, 
this is the crucial step in telling LLMs to return the response the exact way we wanted it.


4. Agent construction.

First of all we decide what LLM to call. As of now we are using ChatGPT, which is good enough to handle not-so-complex use cases. Down
the road we will use GPT4 for more complex cases, and eventually do a drop-in swap with Pristine's finetuned LLM.

```python
        api_key = os.environ.get("OPEN_AI_API")
        GPT_MODEL = "gpt-3.5-turbo-0613"
        llm = ChatOpenAI(
            openai_api_key = api_key,
            model=GPT_MODEL,
            temperature=0
        )
```

Then we assemble all the tools needed:

```python
        tools = [
            GetDataTool(),
            PostProcessTool(),
        ]
```

And give some general instructions to the LLM in terms of system prompt for the agent:

```python
        func_agent_sys_msg = '''You are an awesome assistant in retail. Only make function call to answer questions. You will try your best to figure out four pieces of information:

        1. API to use
        2. Products
        3. Locations
        4. Time Frames

        Leave Product/Location/Time Frame fields blank if you are not sure.

        Some Abbrevations you need to keep in mind:

        W: Week, for example W3 means week 3.
        P: Period, for example P3 means period 3.
        Q: Quarter, for example Q2 means quarter 2.

        And you have to answer the question in two steps: first call api to get data, then use the post process tool to get the final answer. Answer exactly what is being asked, do NOT make any assumption about the metrics asked. Report exactly what the tools returns. And if asked about ratio or percentage, you have to call the same API twice with different flags.
        '''
```

Finally we construct the agent:

```python
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
```

5. A test run with your agent:

```python
        message = "Give me a list of all items which had a cost change in Zone 620 during the last three weeks."
        func_agent.run(message)
```

6. If you want to deploy the agent as a REST API (See the top of this README for how to run it)

This is from the file `iux-app.py`:

```python
        from flask import Flask, request, jsonify
        import sys
        import json
        sys.path.insert(0, './')
        from iux_agent import func_agent as agent

        app = Flask(__name__)

        @app.route('/query', methods=['POST'])
        def add_endpoint():
            data = request.get_json()
            
            if not data or 'prompt' not in data:
                return jsonify({'error': 'Please provide a prompt'}), 400
            
            print(data['prompt'])
            result = agent.run(data['prompt'])

            with open('meta-data.json', 'r') as file:
                meta_data = json.load(file)

            final_res = {'summary': result, 'meta_data': meta_data}

            return jsonify({'result' : final_res})

        if __name__ == '__main__':
            app.run(debug=True, port = 8000, host = '0.0.0.0')
```

7. If you want to deploy your agent as a StreamLit App: (See the top of this README for how to run it)

This is from the file `iux-st-app.py`:

```python
        import openai
        import streamlit as st
        import sys
        import os
        sys.path.insert(0, './')
        from iux_agent import func_agent as agent

        st.title("Pristine Intelligent UI - ChatGPT ")

        openai.api_key = os.environ.get("OPEN_AI_API")

        if "openai_model" not in st.session_state:
            st.session_state["openai_model"] = "gpt-3.5-turbo-0613"

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("What question do you have about your business ?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = agent.run(prompt) 
                message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
```
