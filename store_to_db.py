import argparse
from pathlib import Path

import pandas as pd
import requests
from questdb.ingress import Sender

"""
script to process parameter and measurement data and store it in DB.
Load all Parameters.csv files
Checks each run_id already in the measurement_parameters in DB,
if Yes, skips the run completely to avoid duplicates.
if its not present, ingest that parameter row into measurement_parameters in DB and then
Load that corresponding measurement_file with the run_id and ingest into measurements table in DB.
"""

HOST = "localhost"
PORT = "9000"
QUESTDB_URL = f"http://{HOST}:{PORT}/exec"

COLUMNS_PARAMS = [
    "run_id", "measurement_csv", "mac", "device_name", "duration", "poll_interval", 
    "temperature", "food", "water_amount", "power", "mode", "juice_amount", "duration_setting",
]
NUMERIC_COL_PARAMS = ["duration", "poll_interval", "temperature", "water_amount", "power", "juice_amount", "duration_setting"]
NUMERIC_COL_MEASUREMENTS = [  "power", "apparentpower", "reactivepower", "factor", "voltage", "current" ]


def table_exists():
    sql = """
    CREATE TABLE IF NOT EXISTS measurement_parameters (
        run_id SYMBOL, measurement_csv STRING, mac SYMBOL,device_name SYMBOL, 
        duration DOUBLE, poll_interval DOUBLE, temperature DOUBLE, food STRING,
        water_amount DOUBLE, power DOUBLE, mode SYMBOL, juice_amount DOUBLE, duration_setting DOUBLE, ts TIMESTAMP
    ) timestamp(ts) PARTITION BY DAY WAL;
    """
    try:
        r = requests.get(QUESTDB_URL, params={"query": sql}, timeout=5)
        r.raise_for_status()
        print("QuestDB schema ready")
    except Exception as e:
        print(f"Schema setup failed: {e}")
  
def run_id_exists(run_id):
    query = f"SELECT count(*) FROM measurement_parameters WHERE run_id = '{run_id}'"

    try:
        r = requests.get(QUESTDB_URL, params={"query": query}, timeout=5)
        data = r.json()
        if "dataset" not in data:
            return False
        return data["dataset"][0][0] > 0
    except Exception as e:
        print(f"DB duplicate check failed for run_id {run_id}: {e}")
        return False

def load_params(root_folder):

    files = [f for f in root_folder.rglob("Parameters.csv") if "Test" not in f.parts]

    if not files:
        raise FileNotFoundError("No Parameters.csv files found")
    
    dataframes = []
    print("\n")
    for file in files:
        print(f"Reading {file}")
        df = pd.read_csv(file)
        df = clean_parameters(df)
        dataframes.append(df)
    
    return pd.concat(dataframes, ignore_index=True, sort=False)

def clean_parameters(df):
    df.columns = df.columns.str.strip().str.lower()
    for col in COLUMNS_PARAMS:  #IF ANY EXPECTED COLUMN IS MISSING,ADDES IT WITH NULL VALUES
        if col not in df.columns:
            df[col] = None

    df = df[COLUMNS_PARAMS]
  
    for col in NUMERIC_COL_PARAMS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["ts"] = pd.Timestamp.now(tz="UTC") #ADDES INGESTION TIMESTAMP AS PARAMETER DATA DOESNT HAVE A TIMESTAMP
    df["ts"] = pd.to_datetime(df["ts"], utc=True).astype("datetime64[ns, UTC]")  

    return df

def clean_measurements(df):

    df.columns = [col.lower() for col in df.columns] 
    df["ts"] = pd.to_datetime(df["time"])
    df = df.drop(columns=["time"])
    for col in NUMERIC_COL_MEASUREMENTS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

def ingest_runs(parameters, folder, conf):

    total_parameter_rows = 0
    print("\nProcessing runs from parameters...")

    with Sender.from_conf(conf) as sender:
        for _, row in parameters.iterrows(): 
            param_df = pd.DataFrame([row])
            row = param_df.iloc[0]

            run_id = row["run_id"] 
            measurement_file = row["measurement_csv"]

            if run_id_exists(run_id):
                print(f"Skipping {measurement_file} (run_id {run_id} already exists in DB)")
                continue

            print("run:", run_id)
            sender.dataframe(param_df, table_name="measurement_parameters", at="ts") #INGEST PARAMETERS ROW
            total_parameter_rows += len(param_df)

            file_path = next(folder.rglob(measurement_file), None)
            if file_path is None:
                print(f"WARNING: missing file {measurement_file}")
                continue

            mdf = pd.read_csv(file_path)
            mdf = clean_measurements(mdf)
            mdf["run_id"] = str(run_id)

            sender.dataframe(mdf, table_name="measurements", at="ts") #INGEST CORRESPONDING MEASUREMENT.CSV FILE
            sender.flush()
            

    return total_parameter_rows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--csv-dir",
        default="data_collection",
        help="Folder containing csv files",
    )
    args = parser.parse_args()
    folder = Path(args.csv_dir)

    if not folder.exists():
        raise Exception(f"Folder not found: {folder}")

    conf = f"http::addr={HOST}:{PORT};"
    print(f"Connecting to QuestDB at {HOST}:{PORT}")

    table_exists()
    parameters = load_params(folder)
    total_params = ingest_runs(parameters, folder, conf)

    print(f"\n--- Processing Finished ---\nParameters added: {total_params}")

if __name__ == "__main__":
    main()