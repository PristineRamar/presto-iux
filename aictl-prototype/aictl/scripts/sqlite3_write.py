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


def insert_df_into_sqlite(df, table_name, database_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Get the column names from the DataFrame
    columns = df.columns.tolist()

    # Create the INSERT INTO statement
    insert_statement = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['?'] * len(columns))})"

    # Iterate over each row in the DataFrame
    for _, row in df.iterrows():
        values = row.tolist()
        cursor.execute(insert_statement, values)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


df = pd.read_csv("../../data/primary_log.csv")
insert_df_into_sqlite(df.tail(1), "Log", "../conversations.db")