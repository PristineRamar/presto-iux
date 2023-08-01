import os
import pandas as pd
import sqlite3


def delete_table_if_exists(table_name):
    # Connect to the SQLite database
    # conn = sqlite3.connect("your_database.db")
    cursor = conn.cursor()

    # Check if the table exists
    cursor.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
    )
    result = cursor.fetchone()

    if result is not None:
        # Table exists, so delete it
        cursor.execute(f"DROP TABLE {table_name}")
        print(f"The table '{table_name}' has been deleted.")
    else:
        # Table doesn't exist
        print(f"The table '{table_name}' does not exist.")

    # Commit the changes and close the connection
    conn.commit()


def load_csv_into_sqlite3(csv_filepath, table_name):
    df = pd.read_csv(csv_filepath)
    df.to_sql("df", conn, if_exists="replace")
    conn.execute(
        f"""
        create table if not exists {table_name} as 
        select * from df
        """
    )


if __name__ == "__main__":
    db_filepath = f'{os.environ["HOME"]}/aictl-prototype/conversations.db'
    open(db_filepath, "wb").close()
    conn = sqlite3.connect(db_filepath)
    try:
        delete_table_if_exists("Log")
        log_csv_fp = f'{os.environ["HOME"]}/aictl-prototype/data/primary_log.csv'
        load_csv_into_sqlite3(log_csv_fp, "Log")
    except sqlite3.OperationalError as e:
        print(e)
    try:
        delete_table_if_exists("ApiDesc")
        apidesc_csv_fp = f'{os.environ["HOME"]}/aictl-prototype/data/api_desc.csv'
        load_csv_into_sqlite3(apidesc_csv_fp, "ApiDesc")
    except sqlite3.OperationalError as e:
        print(e)
