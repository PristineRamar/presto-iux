from flask import Flask, request, jsonify, Blueprint
import sys
import json
sys.path.insert(0, './')
#from iux_custom_agent import agent_executor as agent
#from iux_agent import agent_executor as agent
from kvi.kvi_agent import func_agent as agent

app = Flask(__name__)

# Create a blueprint
kvi_blueprint = Blueprint('kvi', __name__)

# Wrap your function into a REST API
#@app.route('/getKVI', methods=['POST'])
@kvi_blueprint.route('/getKVI', methods=['POST'])
def add_endpoint():
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({'error': 'Please provide a prompt'}), 400
    
    print(data['prompt'])
    result = agent.run(data['prompt'])

    with open('meta-data.json', 'r') as file:
        meta_data = json.load(file)

    keywords = ["sorry", "apologize", "error"]
    for keyword in range(len(keywords)):
       if keywords[keyword] in result:
           with open('error-message.json', 'r') as file:
               final_res = json.load(file)
                      
           print(final_res)
           break      
    
    else:
        final_res = {'summary': result, 'meta_data': meta_data}
        print(final_res)
            

    return jsonify({'result' : final_res})

if __name__ == '__main__':
    app.run(debug=True, port = 4012, host = '0.0.0.0')
    #app.run(debug=True, port = 8000, host = '20.228.231.91')
