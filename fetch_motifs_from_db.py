import requests
import pandas as pd
import json

QUESTDB_URL = "http://localhost:9000/exec"

#converts data(string) back to list format
def parse_string_to_list(string_data): 
    return json.loads(string_data)

def json_to_dataframe(query):
    response = requests.get(QUESTDB_URL, params={"query": query})
    response.raise_for_status()
    data = response.json()

    columns = [col["name"] for col in data["columns"]]
    rows = data["dataset"]

    return pd.DataFrame(rows, columns=columns)

def fetch_motifs_1D():

    query = f"""
    SELECT *
    FROM motifs_1D
    """
    #    WHERE device = '{device}' -> optional line, if you want a specific device
    df = json_to_dataframe(query)

    # df["power"] = df["power"].apply(parse_string_to_list)

    return df

def fetch_motifs_multiD():

    query = f"""
    SELECT *
    FROM motifs_multiD
    """
    # WHERE device = '{device}' -> optional line, if you want a specific device
    df = json_to_dataframe(query)

    # multiD_motif = ["power", "apparentpower", "reactivepower", "factor"]
    # for col in multiD_motif:
    #     df[col] = df[col].apply(parse_string_to_list)

    return df
