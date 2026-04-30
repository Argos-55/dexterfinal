"""
3 OLAP insights requeridos.
Corre sobre Parquet (columnar) y exporta resultados como Parquet.

Entrada/salida: ``<repo>/data/duck db/`` (Parquet desde CSV locales vía csv_seed_parquets).
En Docker sigue válido porque ``/analytics/..`` == ``/`` y ``/data`` es el volumen.
"""
from pathlib import Path

import duckdb

from csv_seed_parquets import seed_olap_parquets

DATA_ROOT = Path(__file__).resolve().parent.parent / "data"
INSIGHT_OUT = DATA_ROOT / "duck db"

OLAP_TABLES = [
    "project", "project_status_history", "team", "team_mentor",
    "mentor", "evaluation", "team_participant", "track", "participant",
]


def _duck_sql_path(path: Path) -> str:
    return str(path.resolve()).replace("'", "''")


def _parquet_sources_ready() -> bool:
    """True cuando export_parquet dejó todos los parquet en ``data/*.parquet`` (p. ej. Docker)."""
    return all((DATA_ROOT / f"{t}.parquet").is_file() for t in OLAP_TABLES)


INSIGHT_OUT.mkdir(parents=True, exist_ok=True)
if _parquet_sources_ready():
    SOURCE_DIR = DATA_ROOT
else:
    seed_olap_parquets(DATA_ROOT, INSIGHT_OUT)
    SOURCE_DIR = INSIGHT_OUT

duck = duckdb.connect()

for table in OLAP_TABLES:
    pth = SOURCE_DIR / f"{table}.parquet"
    duck.execute(
        f"""
        CREATE VIEW {table} AS
        SELECT * FROM read_parquet('{_duck_sql_path(pth)}');
        """
    )

print("=" * 60)
print("HACKATHON OLAP ANALYTICS")
print("=" * 60)

print("\n1. Avg transition time: Approved -> Delivered")
q1 = duck.execute(
    """
    WITH approved AS (
        SELECT project_id, changed_at AS approved_at
        FROM project_status_history WHERE status = 'Approved'
    ),
    delivered AS (
        SELECT project_id, changed_at AS delivered_at
        FROM project_status_history WHERE status = 'Delivered'
    )
    SELECT
        COUNT(*) AS projects_analyzed,
        AVG(EXTRACT(EPOCH FROM (d.delivered_at - a.approved_at)) / 86400)::DECIMAL(10,2) AS avg_days,
        MIN(EXTRACT(EPOCH FROM (d.delivered_at - a.approved_at)) / 86400)::DECIMAL(10,2) AS min_days,
        MAX(EXTRACT(EPOCH FROM (d.delivered_at - a.approved_at)) / 86400)::DECIMAL(10,2) AS max_days
    FROM approved a
    JOIN delivered d ON a.project_id = d.project_id
    WHERE d.delivered_at > a.approved_at
    """
).df()
print(q1.to_string(index=False))
q1.to_parquet(str(INSIGHT_OUT / "insight_bottleneck.parquet"))

print("\n2. Participant distribution by hackathon track")
q2 = duck.execute(
    """
    SELECT
        t.name AS track_name,
        COUNT(DISTINCT tp.participant_id) AS total_participants,
        COUNT(DISTINCT tm_t.id) AS total_teams,
        ROUND(COUNT(DISTINCT tp.participant_id) * 100.0 /
              SUM(COUNT(DISTINCT tp.participant_id)) OVER (), 2) AS pct_total
    FROM track t
    JOIN team tm_t ON tm_t.track_id = t.id
    JOIN team_participant tp ON tp.team_id = tm_t.id
    GROUP BY t.name
    ORDER BY total_participants DESC
    """
).df()
print(q2.to_string(index=False))
q2.to_parquet(str(INSIGHT_OUT / "insight_participant_distribution.parquet"))

print("\n3. Top 3 mentors by associated team scores")
q3 = duck.execute(
    """
    WITH mentor_scores AS (
        SELECT
            m.full_name AS mentor_name,
            m.company,
            COUNT(DISTINCT tm.team_id) AS teams_mentored,
            COUNT(e.id) AS total_evaluations,
            AVG(e.score)::DECIMAL(5,2) AS avg_team_score,
            MAX(e.score)::DECIMAL(5,2) AS best_score,
            RANK() OVER (ORDER BY AVG(e.score) DESC) AS ranking
        FROM mentor m
        JOIN team_mentor tm ON tm.mentor_id = m.id
        JOIN project p ON p.team_id = tm.team_id
        JOIN evaluation e ON e.project_id = p.id
        GROUP BY m.id, m.full_name, m.company
    )
    SELECT * FROM mentor_scores WHERE ranking <= 3 ORDER BY ranking
    """
).df()
print(q3.to_string(index=False))
q3.to_parquet(str(INSIGHT_OUT / "insight_top_mentors.parquet"))

duck.close()
print(f"\nOLAP insights exported to {INSIGHT_OUT}/insight_*.parquet")
# Restaurar config de Metabase
