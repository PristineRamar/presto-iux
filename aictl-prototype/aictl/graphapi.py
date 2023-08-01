import lookup.workbook
import pandas as pd


def graph_api_get(url):
    return


def read_cloud_log():
    workbook_id = lookup.workbook.WORKBOOK_ID
    worksheet_name = lookup.workbook.SHEET_NAME_LOG
    url = f"https://graph.microsoft.com/v1.0/me/drive/items/{workbook_id}/workbook/worksheets({worksheet_name})/usedRange"
    log = graph_api_get(url)


def transform_log(headers=None):
    if not headers:
        pass


def json_response_to_csv(rows):
    headers = rows[0]
    df = pd.DataFrame(rows[1:])
    df.columns = headers
    print(df)
    return df


def dataframe_to_json(df):
    headers = df.columns.tolist()
    rows = df.values.tolist()
    return [headers] + rows


def construct_payload(df):
    return {
        "values": dataframe_to_json(df),
        "formulas": [
            [None for _ in range(df.shape[1])] for _ in range(df.shape[0] + 1)
        ],
        "numberFormat": [
            [None for _ in range(df.shape[1])] for _ in range(df.shape[0] + 1)
        ],
    }


def construct_range(df):
    alphas = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    nrows, ncols = df.shape
    return f"A1:{alphas[ncols-1]}{nrows+1}"


def construct_range_for_update(df, prev_num_rows):
    alphas = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    nrows, ncols = df.shape
    return f"A{prev_num_rows+1}:{alphas[ncols-1]}{prev_num_rows + nrows}"
