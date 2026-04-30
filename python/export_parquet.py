"""
Extrae todas las tablas de PostgreSQL y las guarda como Parquet
usando DuckDB como motor de conversion (ZSTD compression).
"""
import os
import duckdb
from pathlib import Path

DATA_DIR = Path("/data")

PG_CONN = (
    f"postgresql://{os.getenv('POSTGRES_USER', 'admin')}"
    f":{os.getenv('POSTGRES_PASSWORD', 'hackathon2024')}"
    f"@{os.getenv('POSTGRES_HOST', 'localhost')}:5432"
    f"/{os.getenv('POSTGRES_DB', 'hackathon')}"
)

TABLES = [
    "hackathon", "track", "participant", "team", "team_participant",
    "mentor", "team_mentor", "project", "project_status_history",
    "judge", "evaluation"
]


def run():
    duck = duckdb.connect()
    duck.execute("INSTALL postgres; LOAD postgres;")
    duck.execute(f"ATTACH '{PG_CONN}' AS pg (TYPE POSTGRES, READ_ONLY);")

    print("Exporting to Parquet...")
    for table in TABLES:
        out = DATA_DIR / f"{table}.parquet"
        duck.execute(
            f"""
            COPY (SELECT * FROM pg.{table})
            TO '{out}' (FORMAT PARQUET, COMPRESSION ZSTD);
            """
        )
        n = duck.execute(f"SELECT COUNT(*) FROM pg.{table}").fetchone()[0]
        print(f"{table}.parquet - {n:,} rows")

    duck.close()
    print("All Parquet files ready in /data/")


if __name__ == "__main__":
    run()
