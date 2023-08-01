import json
from uuid import uuid4

import agent
import app_config

import identity.web
import logctl
import pandas as pd
import requests
from flask import (Flask, jsonify, redirect, render_template, request, session,
                   url_for)
from flask_cors import CORS, cross_origin
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.config.from_object(app_config)
Session(app)
CORS(app)

# This section is needed for url_for("foo", _external=True) to automatically
# generate http scheme when this sample is running on localhost,
# and to generate https scheme when it is deployed behind reversed proxy.
# See also https://flask.palletsprojects.com/en/2.2.x/deploying/proxy_fix/
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
interact = None


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    print(data)
    query = data["message"]
    if not session["cid"] or session["cid"] != data["cid"]:
        session["cid"] = data["cid"]
        session["history"]["cid"] = []
    global interact
    if interact is None:
        interact = agent.create_chatbot_using_api_description()
    _response, history = interact(query, session["history"]["cid"])
    session["history"]["cid"] = history
    response = {
        "status": "ok",
        "message": _response,
    }
    return jsonify(response)


@app.route("/", methods=["GET"])
def chat():
    """
    Renders the chat page and initializes the session.

    This route function is responsible for rendering the chat.html template, which represents the chat page of the application.
    It first retrieves the access token for the user by calling the get_token_for_user function from the auth module, passing the
    required scopes. If there is an error in obtaining the token, it redirects the user to the login page.
    The function then initializes the session by assigning a unique ID to the 'id' key and retrieving the user's display name
    from the user response obtained by making a GET request to the specified endpoint with the access token.
    If a 'cid' parameter is present in the request query parameters, it retrieves the corresponding rows from the log sheet
    and constructs the data dictionary containing the conversation ID and messages. Finally, it renders the chat.html template
    with the data parameter.

    Returns:
        str: The rendered chat.html template.

    Example:
        When the user accesses the '/chat' route, the chat page is rendered with the necessary data.
        If a 'cid' parameter is provided, the corresponding conversation messages are fetched and displayed in the chat page.
    """
    # initialize session
    session["id"] = str(uuid4())
    session["user"] = "You dont get a name"
    cid = request.args.get("cid", default="", type=str)
    session["cid"] = cid
    if "history" not in session:
        session["history"] = {}
    session["history"]["cid"] = cid
    if not cid:
        return render_template("chat.html", data={})


@app.route("/feedback", methods=["POST"])
def feedback():
    return jsonify({
        "status": "ok", "message": "Feedback successfully added!"
    })


@app.route("/export", methods=["POST"])
def export():
    return jsonify({
        "status": "ok", "message": "Export successful!"
    })


@app.route("/update-model", methods=["GET"])
def update_model():
    return jsonify({"status": "ok", "message": "Model updated"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
