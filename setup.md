# setup for data pipeline 

## run docker image of QuestDB

docker run -p 9000:9000 -v "$(pwd):/var/lib/questdb" questdb/questdb:10.0.1

## store the generated csv to the QuestDB

python store_to_db.py
python store_motif.py

## to fetch data from the DB

python fetch_from_db.py
python fetch_motifs_from_db.py







