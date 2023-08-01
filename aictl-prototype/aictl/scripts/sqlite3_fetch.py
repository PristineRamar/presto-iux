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
# Create your connection.
cnx = sqlite3.connect('../conversations.db')
df = pd.read_sql_query("SELECT * FROM Log", cnx)
print(df.columns)
print(df.head())
