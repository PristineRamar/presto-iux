import os
from dotenv import load_dotenv

# manually load environmental variables from .env
load_dotenv(f'{os.environ["HOME"]}/aictl-prototype/aictl/.env')

# Application (client) ID of app registration
CLIENT_ID = os.getenv("CLIENT_ID")
# Application's generated client secret: never check this into source control!
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# You can configure your authority via environment variable
# Defaults to a multi-tenant app in world-wide cloud
AUTHORITY = os.getenv("AUTHORITY", "https://login.microsoftonline.com/common")

# Used for forming an absolute URL to your redirect URI.
REDIRECT_PATH = "/getAToken"
# The absolute URL must match the redirect URI you set
# in the app's registration in the Azure portal.

# You can find more Microsoft Graph API endpoints from Graph Explorer
# https://developer.microsoft.com/en-us/graph/graph-explorer
ENDPOINT = (
    # This resource requires no admin consent
    "https://graph.microsoft.com/v1.0/users"
)

ENDPOINT_DRIVE_LIST = "https://graph.microsoft.com/v1.0/me/drive/root/children"

# ENDPOINT_GET_SHEET = "https://graph.microsoft.com/v1.0/me/drive/items/016MCNA3LZB6HVSYEVMRAYA3Z5VC3MG7RE/workbook/worksheets('zero')/usedRange"
# ENDPOINT_LOG_SHEET_GET_RANGE = "https://graph.microsoft.com/v1.0/me/drive/items/016MCNA3LZB6HVSYEVMRAYA3Z5VC3MG7RE/workbook/worksheets('Log')/usedRange"
ENDPOINT_SHEET_GET_RANGE = "https://graph.microsoft.com/v1.0/me/drive/items/016MCNA3LZB6HVSYEVMRAYA3Z5VC3MG7RE/workbook/worksheets('{}')/usedRange"
ENDPOINT_LOG_SHEET_UPDATE_RANGE = "https://graph.microsoft.com/v1.0/me/drive/items/016MCNA3LZB6HVSYEVMRAYA3Z5VC3MG7RE/workbook/worksheets/Log/range(address='{}')"
ENDPOINT_SYNTHESIZED_SHEET_GET_RANGE = "https://graph.microsoft.com/v1.0/me/drive/items/016MCNA3LZB6HVSYEVMRAYA3Z5VC3MG7RE/workbook/worksheets('Synthesized')/usedRange"
ENDPOINT_USER = "https://graph.microsoft.com/v1.0/me"
ENDPOINT_MESSAGE_SAINUL = "https://graph.microsoft.com/v1.0/chats/19:360b750b-88b9-49bd-94b7-12591a7fe0d9_3f7ff931-fbb0-4e78-a2a0-9853bb16390e@unq.gbl.spaces/messages"
# {
#     "body": {
#         "contentType": "html",
#         "content": "<emoji alt=\"😶‍🌫️\"></emoji>"
#     }
# }

# You can find the proper permission names from this document
# https://docs.microsoft.com/en-us/graph/permissions-reference
SCOPE = ["User.ReadBasic.All", "Files.ReadWrite.All"]

# Tells the Flask-session extension to store sessions in the filesystem
SESSION_TYPE = "filesystem"
# Using the file system will not work in most production systems,
# it's better to use a database-backed session store instead.
