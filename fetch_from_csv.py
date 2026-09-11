import pandas as pd
import warnings
from pathlib import Path


def fetch_from_csv(
    device="Test", num_of_measurements=1, reduce_to_power_per_second=True
):
    """Fetch measurements from CSV files for a given device and number of measurements.´(fetch first x number of measurements, if available)"""
    df = None
    for i in range(1, num_of_measurements + 1):
        csv_path = Path(f"data_collection/{device}/measurement_{device}_{i}.csv")
        if not csv_path.exists():
            print(f"Missing csv file for {device}, measurement {i}") #missing csv file
            continue

        temp = pd.read_csv(csv_path)
        if temp.empty:
            print(f"Empty csv file for {device}, measurement {i}") # empty csv file, due to some measurement error
            continue


        temp = temp[["run_id", "Time", "Power"]].copy() # get relevant columns
        temp["measurement"] = i

        temp["Time"] = pd.to_datetime(temp["Time"])

        if reduce_to_power_per_second: #reduce to power per second -> take mean and interpolate missing values
            temp_1s = (
                temp.set_index("Time")["Power"]
                .resample("1s")
                .mean()
                .interpolate()
                .reset_index()
            ) 
            temp_1s["run_id"] = temp["run_id"].iloc[0] # keep run id for each measurement (just take id in first row)
            temp_1s["measurement"] = i
            if df is None:
                df = temp_1s
            else:
                with warnings.catch_warnings(): # Filter out some future warnings, since they are not relevant for us
                    warnings.filterwarnings(
                        "ignore",
                        category=FutureWarning,
                    )
                    df = pd.concat([df, temp_1s], ignore_index=True)
        else:
            if df is None:
                df = temp
            else:
                with warnings.catch_warnings():
                    warnings.filterwarnings(
                        "ignore",
                        category=FutureWarning,
                    )
                    df = pd.concat([df, temp], ignore_index=True)

    if "Power" in df.columns and "power" not in df.columns: # Standardize column names, since fetching from DB and from CSV gives different names
        df = df.rename(columns={"Power": "power"})

    if "Time" in df.columns and "time" not in df.columns:
        df = df.rename(columns={"Time": "time"})
    return df if df is not None else pd.DataFrame()


def fetch_from_csv_specific_1D(
    device="Test", measurement=1, reduce_to_power_per_second=True
): 
    """get specific measurement from a csv"""
    df = None
    csv_path = Path(f"data_collection/{device}/measurement_{device}_{measurement}.csv")
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing csv file for {device}, measurement {measurement}") #missing csv file
    temp = pd.read_csv(csv_path)
    if temp.empty:
        raise ValueError(f"Empty csv file for {device}, measurement {measurement}") # empty csv file, due to some measurement error

    temp = temp[["run_id", "Time", "Power"]].copy()
    temp["measurement"] = measurement

    temp["Time"] = pd.to_datetime(temp["Time"])

    if reduce_to_power_per_second:
        temp_1s = (
            temp.set_index("Time")["Power"]
            .resample("1s")
            .mean()
            .interpolate()
            .reset_index()
        ) #reduce to power per second -> take mean and interpolate missing values
        temp_1s["run_id"] = temp["run_id"].iloc[0]
        temp_1s["measurement"] = measurement
        if df is None:
            df = temp_1s
        else:
            with warnings.catch_warnings(): # Filter out some future warnings, since they are not relevant for us
                warnings.filterwarnings(
                    "ignore",
                    category=FutureWarning,
                )
                df = pd.concat([df, temp_1s], ignore_index=True)
    else:
        if df is None:
            df = temp
        else:
            with warnings.catch_warnings(): # Filter out some future warnings, since they are not relevant for us
                warnings.filterwarnings(
                    "ignore",
                    category=FutureWarning,
                )
                df = pd.concat([df, temp], ignore_index=True)
    
    if "Power" in df.columns and "power" not in df.columns: # Standardize column names, since fetching from DB and from CSV gives different names
        df = df.rename(columns={"Power": "power"})

    if "Time" in df.columns and "time" not in df.columns:
        df = df.rename(columns={"Time": "time"})
        
    return df if df is not None else pd.DataFrame()

def fetch_from_csv_multiD(
        
    device="Test", num_of_measurements=1, reduce_to_power_per_second=True
):
    df = None
    for i in range(1, num_of_measurements + 1):
        csv_path = Path(f"data_collection/{device}/measurement_{device}_{i}.csv")
        if not csv_path.exists():
            print(f"Missing csv file for {device}, measurement {i}") #missing csv file
            continue

        temp = pd.read_csv(csv_path)
        if temp.empty:
            print(f"Empty csv file for {device}, measurement {i}") # empty csv file, due to some measurement error
            continue
        

        temp = temp[["run_id", "Time", "Power","ApparentPower","ReactivePower", "Factor"]].copy()
        temp["measurement"] = i

        temp["Time"] = pd.to_datetime(temp["Time"])

        if reduce_to_power_per_second:
            temp_1s = (
                temp.set_index("Time")[["Power", "ApparentPower", "ReactivePower", "Factor"]]
                .resample("1s")
                .mean()
                .interpolate()
                .reset_index()
            ) #reduce to power per second -> take mean and interpolate missing values
            temp_1s["run_id"] = temp["run_id"].iloc[0]
            temp_1s["measurement"] = i
            if df is None:
                df = temp_1s
            else:
                with warnings.catch_warnings(): # Filter out some future warnings, since they are not relevant for us
                    warnings.filterwarnings(
                        "ignore",
                        category=FutureWarning,
                    )
                    df = pd.concat([df, temp_1s], ignore_index=True)
        else:
            if df is None:
                df = temp
            else:
                with warnings.catch_warnings():
                    warnings.filterwarnings(
                        "ignore",
                        category=FutureWarning,
                    )
                    df = pd.concat([df, temp], ignore_index=True)
    if "Power" in df.columns and "power" not in df.columns: # Standardize column names, since fetching from DB and from CSV gives different names
        df = df.rename(columns={"Power": "power"})

    if "Time" in df.columns and "time" not in df.columns:
        df = df.rename(columns={"Time": "time"})

    if "ApparentPower" in df.columns and "apparentpower" not in df.columns:
        df = df.rename(columns={"ApparentPower": "apparentpower"})

    if "ReactivePower" in df.columns and "reactivepower" not in df.columns:
        df = df.rename(columns={"ReactivePower": "reactivepower"})
    
    if "Factor" in df.columns and "factor" not in df.columns:
        df = df.rename(columns={"Factor": "factor"})

    return df if df is not None else pd.DataFrame()

def fetch_from_csv_specific_multiD(
    device="Test", measurement=1, reduce_to_power_per_second=True
):
    df = None
    csv_path = Path(f"data_collection/{device}/measurement_{device}_{measurement}.csv")
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing csv file for {device}, measurement {measurement}") #missing csv file
    temp = pd.read_csv(csv_path)
    if temp.empty:
        raise ValueError(f"Empty csv file for {device}, measurement {measurement}") # empty csv file, due to some measurement error

    temp = temp[["run_id", "Time", "Power", "ApparentPower", "ReactivePower", "Factor"]].copy()
    temp["measurement"] = measurement

    temp["Time"] = pd.to_datetime(temp["Time"])

    if reduce_to_power_per_second:
        temp_1s = (
            temp.set_index("Time")[["Power", "ApparentPower", "ReactivePower", "Factor"]]
            .resample("1s")
            .mean()
            .interpolate()
            .reset_index()
        ) #reduce to power per second -> take mean and interpolate missing values
        temp_1s["run_id"] = temp["run_id"].iloc[0]
        temp_1s["measurement"] = measurement
        if df is None:
            df = temp_1s
        else:
            with warnings.catch_warnings(): # Filter out some future warnings, since they are not relevant for us
                warnings.filterwarnings(
                    "ignore",
                    category=FutureWarning,
                )
                df = pd.concat([df, temp_1s], ignore_index=True)
    else:
        if df is None:
            df = temp
        else:
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    category=FutureWarning,
                )
                df = pd.concat([df, temp], ignore_index=True)
    
    if "Power" in df.columns and "power" not in df.columns: # Standardize column names, since fetching from DB and from CSV gives different names
        df = df.rename(columns={"Power": "power"})

    if "Time" in df.columns and "time" not in df.columns:
        df = df.rename(columns={"Time": "time"})

    if "ApparentPower" in df.columns and "apparentpower" not in df.columns:
        df = df.rename(columns={"ApparentPower": "apparentpower"})

    if "ReactivePower" in df.columns and "reactivepower" not in df.columns:
        df = df.rename(columns={"ReactivePower": "reactivepower"})
    
    if "Factor" in df.columns and "factor" not in df.columns:
        df = df.rename(columns={"Factor": "factor"})
        
    return df if df is not None else pd.DataFrame()