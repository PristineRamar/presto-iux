import json
from uuid import uuid4
from flask import abort

import agent
import app_config
import identity
import identity.web
import logctl
import pandas as pd
import requests
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
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

auth = identity.web.Auth(
    session=session,
    authority=app.config["AUTHORITY"],
    client_id=app.config["CLIENT_ID"],
    client_credential=app.config["CLIENT_SECRET"],
)


# interact = agent.create_api_callable()
# interact = agent.create_chatbot_using_api_description()
interact = None
# set domain redirect url
DOMAIN_REDIRECT_URL = "https://aictl.centralindia.cloudapp.azure.com/getAToken"
IS_RUNNING_GUNICORN = None


@app.route("/login")
def login():
    """
    Renders the login page with necessary parameters.

    This route function is responsible for rendering the login.html template, which represents the login page of the application.
    It passes the version number from the identity module as the 'version' parameter to the template. Additionally, it calls
    the log_in function from the auth module to perform the login process. It provides the required scopes and redirect_uri
    as arguments to the log_in function. The scopes define the permissions requested from the user during the login process,
    and the redirect_uri specifies the URL to redirect the user after successful login. The redirect_uri is set as the
    absolute URL for the 'auth_response' route using the 'url_for' function.

    Returns:
        str: The rendered login.html template.

    Example:
        When the user accesses the '/login' route, the login page is rendered with the necessary parameters.
    """
    redirect_uri = url_for("auth_response", _external=True)
    if not app.debug:  # if IS_RUNNING_GUNICORN:
        redirect_uri = DOMAIN_REDIRECT_URL
    return render_template(
        "login.html",
        version=identity.__version__,
        **auth.log_in(
            scopes=app_config.SCOPE,  # Have user consent to scopes during log-in
            redirect_uri=redirect_uri,
        ),
    )


@app.route(app_config.REDIRECT_PATH)
def auth_response():
    """
    Handles the authentication response from the authorization server.

    This route function is responsible for processing the authentication response received from the authorization server.
    It calls the complete_log_in function from the auth module, passing the query parameters from the request as arguments.
    The complete_log_in function processes the response and returns a result dictionary. If the result dictionary contains
    an "error" key, it renders the auth_error.html template, passing the result as a parameter. Otherwise, it redirects
    the user to the 'chat' route using the redirect function from Flask.

    Returns:
        Flask response: Either renders the auth_error.html template or redirects to the 'chat' route.

    Example:
        After the user completes the authentication process, the response is handled by this route.
        If there is an error in the response, the auth_error.html template is rendered with the result.
        Otherwise, the user is redirected to the 'chat' route.
    """
    result = auth.complete_log_in(request.args)
    if "error" in result:
        return render_template("auth_error.html", result=result)
    return redirect(url_for("chat"))


@app.route("/logout")
def logout():
    """
    Performs the logout operation and redirects to the chat page.

    This route function is responsible for performing the logout operation. It calls the log_out function from the auth module,
    passing the URL for the 'chat' route as the argument. The log_out function generates the logout URL based on the provided URL.
    The function then redirects the user to the generated logout URL using the redirect function from Flask.

    Returns:
        Flask response: Redirects the user to the logout URL.

    Example:
        When the user accesses the '/logout' route, the logout operation is performed,
        and the user is redirected to the chat page.
    """
    return redirect(auth.log_out(url_for("chat", _external=True)))


@app.route("/")
def index():
    if not (app.config["CLIENT_ID"] and app.config["CLIENT_SECRET"]):
        # This check is not strictly necessary.
        # You can remove this check from your production code.
        return render_template("config_error.html")
    if not auth.get_user():
        return redirect(url_for("login"))
    return render_template(
        "index.html", user=auth.get_user(), version=identity.__version__
    )


@app.route("/chat", methods=["GET"])
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
    token = auth.get_token_for_user(app_config.SCOPE)
    if "error" in token:
        return redirect(url_for("login"))
    # initialize session
    session["id"] = str(uuid4())
    user_response = requests.get(
        app_config.ENDPOINT_USER,
        headers={"Authorization": "Bearer " + token["access_token"]},
        timeout=30,
    ).json()
    session["user"] = user_response["displayName"]
    # check for named parameters
    cid = request.args.get("cid", default="", type=str)
    session["cid"] = cid
    if "history" not in session:
        session["history"] = {}
    session["history"]["cid"] = cid
    if not cid:
        return render_template("chat.html", data={})
    # get log sheet
    _, _, rows = get_sheet(token)
    # get rows corresponding to cid
    messages = logctl.get_rows_by_cid(rows, cid)
    data = {"conversationId": cid, "messages": messages}
    return render_template("chat.html", data=data)


@app.route("/call_downstream_api")
def call_downstream_api():
    token = auth.get_token_for_user(app_config.SCOPE)
    if "error" in token:
        return redirect(url_for("login"))
    # Use access token to call downstream api
    api_result = requests.get(
        app_config.ENDPOINT,
        headers={"Authorization": "Bearer " + token["access_token"]},
        timeout=30,
    ).json()
    return render_template("display.html", result=api_result)


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
        token = auth.get_token_for_user(app_config.SCOPE)
        if "error" in token:
            return redirect(url_for("login"))
        _, _, rows = get_sheet(token, "api_description")
        interact = agent.create_chatbot_using_api_description(rows)
    _response, history = interact(query, session["history"]["cid"])
    session["history"]["cid"] = history
    response = {
        "status": "ok",
        "message": _response,
    }
    return jsonify(response)


@app.route("/update-model", methods=["GET"])
def update_model():
    """
    Updates the model used by the chatbot.

    This route function is responsible for updating the model used by the chatbot. It first retrieves the access token for the user
    by calling the get_token_for_user function from the auth module, passing the required scopes. If there is an error in obtaining
    the token, it redirects the user to the login page.
    The function then makes a GET request to the specified endpoint to retrieve the synthesized sheet range, which contains the text
    data for updating the model. The response is stored in the 'response' variable.
    The global 'interact' variable, which represents the chatbot interaction model, is updated with the text data from the response.
    Finally, it returns a JSON response indicating the success of the model update.

    Returns:
        dict: A JSON response indicating the status and message.

    Example:
        When the user accesses the '/update-model' route, the model used by the chatbot is updated with the latest text data.
    """
    token = auth.get_token_for_user(app_config.SCOPE)
    if "error" in token:
        return redirect(url_for("login"))
    response = requests.get(
        app_config.ENDPOINT_SYNTHESIZED_SHEET_GET_RANGE,
        headers={"Authorization": "Bearer " + token["access_token"]},
        timeout=30,
    ).json()
    print(response)
    global interact
    interact = agent.update_model(response["text"])
    return jsonify({"status": "ok", "message": "Model updated"})


@app.route("/feedback", methods=["POST"])
def feedback():
    """
    Handles the feedback provided by the user for a conversation.

    This route function is responsible for handling the feedback provided by the user for a conversation. It first verifies that the
    user is logged in by retrieving the access token using the get_token_for_user function from the auth module and checking for any
    errors. If there is an error in obtaining the token, it redirects the user to the login page.
    The function then retrieves the conversation data from the request's JSON payload. The "log" sheet is fetched from the cloud
    using the get_sheet function, and the necessary server-side information is injected into the data.
    The feedback is added to the relevant rows in the log and a payload containing the updated rows is created.
    The conversation is patched in the log by calling the patch_conversation function with the access token, the feedback payload,
    and the range address.
    Finally, it returns a JSON response indicating the success of adding the feedback.

    Returns:
        dict: A JSON response indicating the status and message.

    Example:
        When the user submits feedback for a conversation through the '/feedback' route, the feedback is added to the log and the
        conversation is patched.
    """
    # verify the user is logged in
    token = auth.get_token_for_user(app_config.SCOPE)
    if "error" in token:  # back to the login page with you
        return redirect(url_for("login"))
    # get conversation data from user
    data = request.get_json()
    # get "log" sheet from cloud
    logresp, nrows, rows = get_sheet(token, sheet_name="log")
    # inject server-side information
    data["user"] = session["user"]
    data["SessionId"] = session["id"]
    # add feedback to relevant rows and create updated rows payload
    fbpayload, alpha_range = logctl.add_feedback_to_conversation(rows, data, nrows)
    print(fbpayload)
    # patch conversation to log
    patchresp = patch_conversation(token, fbpayload, alpha_range)
    print(patchresp)
    return jsonify({"status": "ok", "message": "Feedback successfully added!"})


def export_conversation(token, data, nrows):
    """
    Exports the conversation to the log sheet.

    This function is responsible for exporting the conversation data to the log sheet. It first injects the necessary server-side
    information into the data, including the user and session ID.
    The payload and cell address range for export are prepared by calling the prepare_export_payload function from the logctl module.
    Finally, the conversation is patched to the log sheet by calling the patch_conversation function with the access token, payload,
    and range address.

    Args:
        token (str): The access token for the user.
        data (dict): The conversation data to be exported.
        nrows (int): The number of rows in the log sheet.

    Returns:
        dict: The response of the PATCH request.

    Example:
        export_conversation(token, data, nrows) exports the conversation to the log sheet, updating the log with the new data.
    """
    # inject server-side information
    data["user"] = session["user"]
    data["SessionId"] = session["id"]
    # prepare payload and cell address range for export
    payload, alpha_range = logctl.prepare_export_payload(data, nrows)
    # PATCH conversation to log sheet
    return patch_conversation(token, payload, alpha_range)


def patch_conversation(token, payload, alpha_range):
    """
    Updates the conversation in the log sheet.

    This function is responsible for updating the conversation in the log sheet. It makes a PATCH request to the specified endpoint
    with the payload containing the updated values and the range address to update. The request is authenticated using the access
    token provided.

    Args:
        token (str): The access token for the user.
        payload (list): The updated values to be patched.
        alpha_range (str): The range address to update in the log sheet.

    Returns:
        dict: The response of the PATCH request.

    Example:
        patch_conversation(token, payload, alpha_range) updates the conversation in the log sheet with the provided payload,
        affecting the specified range of cells.
    """
    return requests.patch(
        url=app_config.ENDPOINT_LOG_SHEET_UPDATE_RANGE.format(alpha_range),
        data=json.dumps({"values": payload}),
        headers={
            "Authorization": "Bearer " + token["access_token"],
            "Content-type": "application/json",
        },
        timeout=30,
    ).json()


def get_sheet(token, sheet_name="log"):
    """
    Retrieves the log sheet from the cloud.

    This function is responsible for retrieving the log sheet from the cloud. It makes a GET request to the specified endpoint with
    the access token provided for authentication. The response is stored in the 'response' variable and contains information about
    the log sheet, including the row count and text data.

    Args:
        token (str): The access token for the user.
        sheet_name (str, optional): The name of the sheet to retrieve. Defaults to "log".

    Returns:
        tuple: A tuple containing the response, the number of rows in the log sheet, and the text data.

    Example:
        get_sheet(token, sheet_name="log") retrieves the log sheet from the cloud, providing information about the sheet and
        its contents.
    """
    r = requests.get(
        app_config.ENDPOINT_SHEET_GET_RANGE.format(sheet_name),
        headers={"Authorization": "Bearer " + token["access_token"]},
        timeout=30,
    )
    response = r.json()
    print("get_sheet response:", r.status_code)
    if r.status_code != 200:
        abort(404)
    nrows = response["rowCount"]
    text = response["text"]
    return response, nrows, text


@app.route("/export", methods=["POST"])
def export():
    """
    Exports the conversation data to the log sheet.

    This route function is responsible for exporting the conversation data to the log sheet. It first verifies that the user is logged
    in by retrieving the access token using the get_token_for_user function from the auth module and checking for any errors. If there
    is an error in obtaining the token, it redirects the user to the login page.
    The function then retrieves the conversation data from the request's JSON payload. The "log" sheet and its metadata are fetched
    using the get_sheet function.
    The conversation data is exported to the log sheet by calling the export_conversation function with the access token, the data,
    and the number of rows in the log sheet.
    Finally, it returns a JSON response indicating the success of the export.

    Returns:
        dict: A JSON response indicating the status and message.

    Example:
        When the user submits conversation data for export through the '/export' route, the data is exported to the log sheet.
    """
    # verify the user is logged in
    token = auth.get_token_for_user(app_config.SCOPE)
    if "error" in token:  # back to the login page with you
        return redirect(url_for("login"))
    # get POST parameters
    data = request.get_json()
    # get the "log" sheet and metadata
    logresp, nrows, rows = get_sheet(token, sheet_name="log")
    # export conversation data
    patchresp = export_conversation(token, data, nrows)
    return jsonify({"status": "ok", "message": "None"})


if __name__ == "__main__":
    app.run()
else:  # running with gunicorn
    IS_RUNNING_GUNICORN = True
