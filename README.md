# Power Data ETL Pipeline

This project implements an ETL (Extract, Transform, Load) pipeline for processing power-consumption data and discovered device motifs.

The pipeline uses Python, Pandas, QuestDB, Docker to store, retrieve, and manage time-series measurement data and motifs.

## ETL Workflow

```text
IoT Power Data
      │
      ▼
   Extract
      │
      ▼
CSV / Python
      │
      ▼
 Transform
(Pandas / NumPy)
      │
      ▼
    Load
      │
      ▼
   QuestDB
      │
      ▼
Motif Discovery
      │
      ▼
Store / Retrieve Motifs
```

## Project Structure

```text
ETL/
│
├── discovered_motifs_1D.csv
├── discovered_motifs_multiD.csv
│
├── fetch_from_db.py
├── fetch_motifs_from_db.py
├── store_to_db.py
├── store_motif.py
│
├── setup.md
└── README.md
```

## Files
### store_to_db.py

Loads measurement data into QuestDB.
This represents the Load stage of the ETL pipeline after the collected data has been processed.

### fetch_from_db.py

Retrieves stored power-consumption/time-series data from QuestDB for further processing and analysis.

### store_motif.py

Stores discovered motifs in QuestDB.
The motifs represent characteristic patterns found in device power-consumption data.

### fetch_motifs_from_db.py

Retrieves previously stored motifs from QuestDB.
These motifs can be used for comparison, visualization, and device identification.

### discovered_motifs_1D.csv

Contains motifs discovered using one-dimensional analysis, primarily based on power-consumption data.

### discovered_motifs_multiD.csv

Contains motifs discovered using multi-dimensional analysis, using multiple electrical measurements such as:

- Power
- Apparent power
- Reactive power
- Power factor
- Voltage
- Current

- setup.md

Contains instructions for setting up the project environment and required services.

## Technologies

- Python — ETL scripts and data processing
- Pandas — data manipulation and transformation
- QuestDB — time-series database
- Docker — running the QuestDB environment