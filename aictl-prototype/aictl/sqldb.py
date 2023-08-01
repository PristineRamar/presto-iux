# Log(
#   "SessionId" TEXT,
#   "ConversationId" TEXT,
#   "UtteranceIndex" TEXT,
#   "Utterance" TEXT,
#   "Role" TEXT,
#   "Type" TEXT,
#   "CreatedBy" TEXT,
#   "CreationTime" TEXT,
#   "UseForTraining" TEXT,
#   "Category" TEXT
# );

import sqlite3
import pandas as pd
import os

LOG_TABLE_NAME = "Log"
APIDESC_TABLE_NAME = "ApiDesc"
SQLITE3_DB_PATH = os.path.join(os.environ["HOME"], "aictl-prototype/conversations.db")


def get_conversation_by_id(conversation_id):
    # Create your connection.
    cnx = sqlite3.connect(SQLITE3_DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM {LOG_TABLE_NAME}", cnx)
    df = df[df.ConversationId == conversation_id]
    # return df.to_dict("tight")["data"]
    messages = []
    for _, row in df.iterrows():
        messages.append(
            {"role": row["Role"], "textContent": row["Utterance"].replace('"', "'")}
        )
    cnx.close()
    return messages


def get_apidesc():
    cnx = sqlite3.connect(SQLITE3_DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM {APIDESC_TABLE_NAME}", cnx)
    cnx.close()
    return [df.columns.tolist()] + df.to_dict("tight")["data"]


def insert_conversation(df):
    conn = sqlite3.connect(SQLITE3_DB_PATH)
    cursor = conn.cursor()

    # Get the column names from the DataFrame
    columns = df.columns.tolist()

    # Create the INSERT INTO statement
    insert_statement = f"INSERT INTO Log ({', '.join(columns)}) VALUES ({', '.join(['?'] * len(columns))})"

    # Iterate over each row in the DataFrame
    for _, row in df.iterrows():
        values = row.tolist()
        cursor.execute(insert_statement, values)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def add_feedback(conversation_id, use_for_training):
    cnx = sqlite3.connect(SQLITE3_DB_PATH)
    cursor = cnx.cursor()
    query = f"""
    UPDATE Log
    SET UseForTraining = '{use_for_training}'
    WHERE ConversationId = '{conversation_id}'
    """
    cursor.execute(query)
    cnx.commit()
    cnx.close()


def handle_feedback(data):
    conversation_id = data["cid"]
    rows = get_conversation_by_id(conversation_id)
    # verify that the conversation doesn't exist
    if len(rows) > 0:
        add_feedback(conversation_id, use_for_training=data["useForTraining"])
        return
    df = translate_user_data(data)
    insert_conversation(df)


def translate_user_data(data):
    # {
    #     "data": [
    #         {
    #             "message": "Welcome! How can I help you with your inquiries?",
    #             "utteranceIndex": 0,
    #             "role": "AI",
    #         },
    #         {
    #             "message": "Give me the primary KVIs at Wisconsin.",
    #             "utteranceIndex": 1,
    #             "role": "User",
    #         },
    #         {
    #             "message": "KVI = KVI_api(product_cateogry= '', location_name = 'Wisconsin', type = 'Primary')",
    #             "utteranceIndex": 2,
    #             "role": "AI",
    #         },
    #     ],
    #     "cid": "cd1b703a-73ab-4482-9e2f-51845f2b2389",
    #     "useForTraining": "yes",
    #     "timestamp": "Wed Jun 07 2023 15:49:45 GMT+0530 (India Standard Time)",
    #     "user": "",
    #     "SessionId": "e6810d10-739f-4268-ad76-d6639b792560",
    # }
    # ---------------------------------------------------------------------------
    # Log Table Schema
    # ================
    # CREATE TABLE Log(
    #   "index" INT,
    #   SessionId TEXT,
    #   ConversationId TEXT,
    #   UtteranceIndex INT,
    #   Utterance TEXT,
    #   Role TEXT,
    #   Type TEXT,
    #   CreatedBy TEXT,
    #   CreationTime TEXT,
    #   UseForTraining TEXT,
    #   Category REAL
    # );
    rows = []
    for i, message in enumerate(data["data"]):
        rows.append(
            {
                "SessionId": data["SessionId"],
                "ConversationId": data["cid"],
                "UtteranceIndex": i,
                "Utterance": message["message"],
                "Role": message["role"],
                "Type": "NA",
                "CreatedBy": data["user"],
                "CreationTime": data["timestamp"],
                "UseForTraining": data["useForTraining"],
                "Category": "NA",
            }
        )
    return pd.DataFrame(rows)
