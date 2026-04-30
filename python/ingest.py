"""
Bulk ingestion usando COPY_FROM (mas rapido que INSERT).
Inserta en orden respetando FK constraints.
"""
import os
import psycopg2
from pathlib import Path

DATA_DIR = Path("/data")


def get_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        dbname=os.getenv("POSTGRES_DB", "hackathon"),
        user=os.getenv("POSTGRES_USER", "admin"),
        password=os.getenv("POSTGRES_PASSWORD", "hackathon2024"),
        port=5432,
    )


def copy_csv(cursor, table: str, filepath: Path, columns: list):
    # Use PostgreSQL CSV parser to handle quoted commas/arrays safely.
    cols = ", ".join(columns)
    sql = (
        f"COPY {table} ({cols}) FROM STDIN WITH "
        "CSV HEADER DELIMITER ',' QUOTE '\"' NULL ''"
    )
    with open(filepath, "r", newline="") as f:
        cursor.copy_expert(sql=sql, file=f)
    print(f"Loaded {table}")


def run():
    conn = get_conn()
    conn.autocommit = False
    cur = conn.cursor()

    try:
        print("Starting bulk ingestion...")

        copy_csv(cur, "hackathon", DATA_DIR / "hackathons.csv", ["id", "name", "edition", "start_date", "end_date", "location", "max_team_size"])
        copy_csv(cur, "track", DATA_DIR / "tracks.csv", ["id", "hackathon_id", "name", "description"])
        copy_csv(cur, "participant", DATA_DIR / "participants.csv", ["id", "hackathon_id", "full_name", "email", "skills", "university", "country", "registered_at"])
        copy_csv(cur, "team", DATA_DIR / "teams.csv", ["id", "hackathon_id", "track_id", "name"])
        copy_csv(cur, "team_participant", DATA_DIR / "team_participants.csv", ["team_id", "participant_id", "role"])
        copy_csv(cur, "mentor", DATA_DIR / "mentors.csv", ["id", "full_name", "email", "expertise", "company", "max_teams"])
        copy_csv(cur, "team_mentor", DATA_DIR / "team_mentors.csv", ["team_id", "mentor_id"])

        cur.execute("ALTER TABLE project DISABLE TRIGGER ALL;")
        copy_csv(cur, "project", DATA_DIR / "projects.csv", ["id", "team_id", "title", "description", "repo_url", "current_status"])
        copy_csv(cur, "project_status_history", DATA_DIR / "project_status_history.csv", ["id", "project_id", "status", "changed_at", "changed_by", "notes"])
        cur.execute("ALTER TABLE project ENABLE TRIGGER ALL;")

        copy_csv(cur, "judge", DATA_DIR / "judges.csv", ["id", "full_name", "email", "expertise"])
        copy_csv(cur, "evaluation", DATA_DIR / "evaluations.csv", ["id", "project_id", "judge_id", "score", "feedback"])

        for seq_table in ["hackathon", "track", "participant", "team", "mentor", "project", "project_status_history", "judge", "evaluation"]:
            cur.execute(f"SELECT setval('{seq_table}_id_seq', MAX(id)) FROM {seq_table};")

        conn.commit()
        print("Ingestion complete!")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    run()
