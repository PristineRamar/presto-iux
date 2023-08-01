import logging
from uuid import uuid4

import agent
import requests
import sqldb as db
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_cors import CORS, cross_origin
from flask_session import Session

app = Flask(__name__)
app.secret_key = "unbelievablysecretkeydude"
app.config["SESSION_TYPE"] = "filesystem"

Session(app)
CORS(app)

# Configure the logging
logging.basicConfig(
    filename="goldilocks.log",
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def _log(key, value, level="debug"):
    levels = {"debug": 10, "info": 20, "warn": 30, "error": 40, "critical": 50}
    logging.log(levels[level], f"{key}: {value}")


interact_with_llm = None


@app.route("/")
def index():
    return redirect(url_for("chat"))


@app.route("/chat", methods=["GET"])
def chat():
    logging.debug(request.__dict__)
    _log("request headers", request.headers)
    # check for named parameters
    cid = request.args.get("cid", default="", type=str)
    username = request.args.get("username", default="", type=str)
    # initialize session
    session["id"] = str(uuid4())
    session["user"] = username
    session["cid"] = cid
    for key in ["id", "user", "cid"]:
        _log(key, session[key])
    # create session history if necessary
    if "history" not in session:
        session["history"] = {}
    # set cid in session history
    session["history"]["cid"] = cid
    _log("session.history", session.get("history"))
    if not cid:
        _log("Event", "No conversatoin ID; Opening /chat template with data={}", "info")
        return render_template("chat.html", data={})
    # get rows corresponding to cid
    messages = db.get_conversation_by_id(cid)
    data = {"conversationId": cid, "messages": messages}
    _log("Event", f"Opening /chat template with data={data}", "info")
    return render_template("chat.html", data=data)


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    _log("Request", request.__dict__)
    _log("Request Headers", request.headers)
    _log("POST request parameters", data)
    # get query from user
    query = data["message"]
    _log("User Query", query, "info")

    # set conversation ID if provided by the user
    if not session["cid"] or session["cid"] != data["cid"]:
        session["cid"] = data["cid"]
        session["history"]["cid"] = []
        _log("CID", session["cid"])

    # create chat model if it doesn't exist already
    global interact_with_llm
    if interact_with_llm is None:
        rows = db.get_apidesc()
        _log("Rows from ApiDesc table", rows, "info")
        interact_with_llm = agent.create_chatbot_using_api_description(rows)

    _response, history = interact_with_llm(query, session["history"]["cid"])
    _log("AI response", _response, "info")
    _log("Conversation history", history, "debug")
    session["history"]["cid"] = history
    response = {
        "status": "ok",
        "message": _response,
    }
    _log("Response to client", response, "info")
    return jsonify(response)


@app.route("/feedback", methods=["POST"])
def feedback():
    _log("Request Headers", request.headers, "debug")
    _log("Request", request.__dict__, "debug")
    # get conversation data from user
    data = request.get_json()
    _log("POST method /feedback parameters", data, "info")
    # inject server-side information
    data["user"] = session["user"]
    data["SessionId"] = session["id"]
    _log("Inject session variables into user data", data, "debug")
    # send feedback to database
    db.handle_feedback(data)
    return jsonify({"status": "ok", "message": "Feedback successfully added!"})


if __name__ == "__main__":
    app.run(host="localhost", port=5001, debug=True)
else:
    print("Running via *gunicorn*")
    # initializations for gunicorn
