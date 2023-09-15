from flask import Flask, request, jsonify, Blueprint
import sys
import json

sys.path.insert(0, '/')

#from iux_custom_agent import agent_executor as agent
#from iux_agent import agent_executor as agent
from recommendation.recommendation_agent import func_agent as agent


app = Flask(__name__)

# Create a blueprint
recommendationservice_blueprint = Blueprint('recommend-review-approve', __name__)

# Wrap your function into a REST API
@recommendationservice_blueprint.route('/recommend-review-approve-service', methods=['POST'])
def add_endpoint():
    data = request.get_json()
    print("Generic prompts")
    if not data or 'prompt' not in data:
        return jsonify({'error': 'Please provide a prompt'}), 400
    
    # May want to modify prompt based on context + priors
    prompt = data['prompt']    
    user_id = data['user-id']
    print('prompt', data['prompt'])
    print('user id ',data['user-id'])
    print(f'The user id is {user_id}')
    result = agent.run(data['prompt'] + f'The user id is {user_id}')
    print('result ',result)
   # response_data = json.dumps({'result' : result})
    final_res = {'summary': result}
    return final_res
                   
'''
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
'''
   


if __name__ == '__main__':
    app.debug=True
    app.run( port = 9512, host = '0.0.0.0')
 

