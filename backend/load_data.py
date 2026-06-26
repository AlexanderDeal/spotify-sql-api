import pandas as pd
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent
csv_path = BASE_DIR / "track_data_final.csv"
df  = pd.read_csv(csv_path)

df['explicit'] = df['explicit'].map({True:1, False:0})
df['track_duration_seconds'] = df['track_duration_ms'] / 1000

db_path = BASE_DIR / "spotify.db"
connection = sqlite3.connect(db_path)

df.to_sql("tracks", connection, if_exists="replace", index=False)

print(f"Done! {len(df)} rows loaded into tracks table.")

connection.close()

