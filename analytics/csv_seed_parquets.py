"""Genera los Parquet de entrada para OLAP desde los CSV en data/."""
from __future__ import annotations

from pathlib import Path

import duckdb

OLAP_CSV_SOURCES = {
    "project": "projects.csv",
    "project_status_history": "project_status_history.csv",
    "team": "teams.csv",
    "team_mentor": "team_mentors.csv",
    "mentor": "mentors.csv",
    "evaluation": "evaluations.csv",
    "team_participant": "team_participants.csv",
    "track": "tracks.csv",
    "participant": "participants.csv",
}


def _sql_path(p: Path) -> str:
    return str(p.resolve()).replace("'", "''")


def seed_olap_parquets(data_root: Path, parquet_out: Path) -> None:
    parquet_out.mkdir(parents=True, exist_ok=True)
    duck = duckdb.connect()
    try:
        for table, csv_name in OLAP_CSV_SOURCES.items():
            csv_path = data_root / csv_name
            if not csv_path.is_file():
                raise FileNotFoundError(f"No se encontró {csv_path}")
            pq_path = parquet_out / f"{table}.parquet"
            c = _sql_path(csv_path)
            o = _sql_path(pq_path)
            duck.execute(
                f"""
                COPY (
                    SELECT * FROM read_csv_auto(
                        '{c}',
                        header=true,
                        sample_size=-1
                    )
                ) TO '{o}' (FORMAT PARQUET, COMPRESSION ZSTD)
                """
            )
    finally:
        duck.close()
