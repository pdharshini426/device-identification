import requests
import pandas as pd
import numpy as np

QUESTDB_URL = "http://localhost:9000/exec"

def fetch_measurements(limit=np.inf, device="Kettle", reduce_to_power_per_second=True):

    if not np.isfinite(limit):
        query_limit = ""
    else:
        query_limit = f"LIMIT {limit}"

    query = f"""    SELECT m.*
    FROM measurements m JOIN measurement_parameters p ON m.run_id = p.run_id
    WHERE p.device_name ILIKE '{device}'
    {query_limit}
    """

    response = requests.get(
        QUESTDB_URL,
        params={"query": query}
    )
    response.raise_for_status()

    # Convert JSON response
    data = response.json()

    # Extract column names
    columns = [
        col["name"]
        for col in data["columns"]
    ]

    # Extract rows
    rows = data["dataset"]

    # Create DataFrame
    df = pd.DataFrame(
        rows,
        columns=columns
    )

    if "Power" in df.columns and "power" not in df.columns: # Standardize column names, since fetching from DB and from CSV gives different names
        df = df.rename(columns={"Power": "power"})

    if "Time" in df.columns and "time" not in df.columns: # Standardize column names, since fetching from DB and from CSV gives different names
        df = df.rename(columns={"Time": "time"})
    
    if "timestamp" in df.columns: # Standardize column names, since fetching from DB and from CSV gives different names
        df = df.rename(columns={"timestamp": "time"})

    if "ApparentPower" in df.columns and "apparent_power" not in df.columns: # Standardize column names, since fetching from DB and from CSV gives different names
        df = df.rename(columns={"ApparentPower": "apparentpower"})

    if "ReactivePower" in df.columns and "reactivepower" not in df.columns: # Standardize column names, since fetching from DB and from CSV gives different names
        df = df.rename(columns={"ReactivePower": "reactivepower"})
    
    if "Factor" in df.columns and "factor" not in df.columns:
        df = df.rename(columns={"Factor": "factor"})

    df = df.loc[:, ~df.columns.duplicated()]


    if reduce_to_power_per_second:
        required_columns = {"time", "power", "run_id"}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            raise Exception(f"Missing required columns for resampling: {sorted(missing_columns)}")

        df["time"] = pd.to_datetime(df["time"], errors="coerce")

        print(df["time"].head(10))
        print(df["time"].isna().sum())
        df = df.dropna(subset=["time"])
        resampled_frames = []
        for _, group in df.sort_values("time").groupby("run_id", sort=False):
            temp_1s = (
                group.set_index("time")
                .resample("1s")
                .mean(numeric_only=True)
                .interpolate()
                .reset_index()
            )
            temp_1s["run_id"] = group["run_id"].iloc[0]
            resampled_frames.append(temp_1s)

        df = pd.concat(resampled_frames, ignore_index=True) if resampled_frames else pd.DataFrame()
        
    return df

if __name__ == "__main__":

    print("\nFetching data from QuestDB...\n")

    df = fetch_measurements(
        limit=np.inf,
        device="Kettle",
    )

    print(df.head())
    print(f"\nRows fetched: {len(df)}")

    print("\nColumns:")
    print(df.columns)