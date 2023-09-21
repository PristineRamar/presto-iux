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
    result = agent.run(data['prompt'] + f'The user id is {user_id}')
    print('result ',result)
   # response_data = json.dumps({'result' : result})
    final_res = {'summary': result}
    print(final_res)
    return json.dumps({'result' : final_res})
        
                   
   


if __name__ == '__main__':
    app.debug=True
    app.run( port = 9512, host = '0.0.0.0')
 

