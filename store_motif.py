import argparse
from pathlib import Path
import pandas as pd
import requests
from questdb.ingress import Sender
from store_to_db import HOST, PORT, QUESTDB_URL

def load_data(folder):

    folder = Path(folder)
    file_1 = folder / "discovered_motifs_1D.csv"
    file_2 = folder / "discovered_motifs_multiD.csv"
    
    if not file_1.exists():
        raise FileNotFoundError(f"Missing: {file_1}")

    if not file_2.exists():
        raise FileNotFoundError(f"Missing: {file_2}")

    df1 = pd.read_csv(file_1)
    df2 = pd.read_csv(file_2)

    df1.columns = df1.columns.str.lower()
    df2.columns = df2.columns.str.lower()

    df1["time"], df2["time"] = pd.Timestamp.now(tz="UTC"), pd.Timestamp.now(tz="UTC")
    df1["time"] = pd.to_datetime(df1["time"], utc=True).astype("datetime64[ns, UTC]")
    df2["time"] = pd.to_datetime(df2["time"], utc=True).astype("datetime64[ns, UTC]")

    return df1, df2

#create two tables in QuestDB for storing 1D and multiD motifs
def create_tables():
    drop_table = 'DROP TABLE IF EXISTS motifs_1D;'
    drop_table_multiD = 'DROP TABLE IF EXISTS motifs_multiD;'

    create_table = """
    CREATE TABLE motifs_1D (
        device SYMBOL,
        motif_number INT,
        power STRING,
        window_size INT,
        time TIMESTAMP
    ) TIMESTAMP(time) PARTITION BY DAY WAL;
    """

    create_table_multiD = """
    CREATE TABLE motifs_multiD (
        device SYMBOL,
        motif_number INT,
        power STRING,
        apparentpower STRING,
        reactivepower STRING,
        factor STRING,
        window_size INT,
        time TIMESTAMP
    ) TIMESTAMP(time) PARTITION BY DAY WAL;
    """

    try:
        
        r1 = requests.get(QUESTDB_URL, params={"query": drop_table}, timeout=5)
        r1.raise_for_status()

        r2 = requests.get(QUESTDB_URL, params={"query": drop_table_multiD}, timeout=5)
        r2.raise_for_status()

        r3 = requests.get(QUESTDB_URL, params={"query": create_table}, timeout=5)
        r3.raise_for_status()

        r4 = requests.get(QUESTDB_URL, params={"query": create_table_multiD}, timeout=5)
        r4.raise_for_status()

        print("QuestDB schema for motifs are ready")

    except Exception as e:
        print(f"Schema setup failed: {e}")

def ingest(df1, df2, conf):
    with Sender.from_conf(conf) as sender:
        sender.dataframe(df1, table_name="motifs_1D", at="time") 
        sender.dataframe(df2, table_name="motifs_multiD", at="time") 
        sender.flush()
    print("Motifs ingested successfully")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--csv-dir",
        default="data_collection",
        help="Folder containing csv files",
    )
    args = parser.parse_args()
 
    df1, df2 = load_data(args.csv_dir)
 
    create_tables()

    conf = f"http::addr={HOST}:{PORT};"
    ingest(df1, df2,conf)

if __name__ == "__main__":
    main()