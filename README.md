# Hackathon Management Platform

Proyecto base para levantar PostgreSQL + pipeline Python + Metabase con un solo comando.

## Quick start

```bash
docker-compose up --build
```

## Estructura

- `sql/`: esquema, triggers, stored procedure e indices.
- `python/`: generacion de CSV, ingesta con COPY y export Parquet.
- `analytics/`: consultas OLAP sobre Parquet con DuckDB.
- `data/`: artefactos generados (CSV, Parquet e insights).
- `docs/`: diagrama ER.

Metabase URL: http://localhost:3000
Puerto Metabase: 3000
Credenciales de BD que usa Metabase internamente:
POSTGRES_USER=admin
POSTGRES_PASSWORD=hackathon2024
POSTGRES_DB=hackathon (y también usa la DB metabase para su app metadata)

Acceso a los otros entregables
PostgreSQL: localhost:5432
Usuario: admin
Password: hackathon2024
DB: hackathon

Artefactos generados: carpeta data/ (CSV, Parquet, insights)
Consultas OLAP: scripts en analytics/
SQL (schema/triggers/SP/índices): sql/
Diagrama ER: docs/er_diagram.md




Paso 1 — Crear las 3 preguntas (Questions)
Ve a New → Question → SQL query y pega cada una:
Q1 — Project Pipeline (status funnel)
sqlSELECT current_status, COUNT(*) AS total
FROM project
GROUP BY current_status
ORDER BY ARRAY_POSITION(
  ARRAY['Idea','Approved','In Development','Delivered','Evaluated'],
  current_status
);
→ Visualización: Bar chart. Guarda como "Project Pipeline"
Q2 — Bottleneck: días entre transiciones
sqlSELECT
  h.status AS from_status,
  d.status AS to_status,
  ROUND(AVG(EXTRACT(EPOCH FROM (d.changed_at - h.changed_at)) / 86400), 1) AS avg_days
FROM project_status_history h
JOIN project_status_history d
  ON h.project_id = d.project_id AND d.changed_at > h.changed_at
WHERE (h.status, d.status) IN (
  ('Idea','Approved'),
  ('Approved','In Development'),
  ('In Development','Delivered'),
  ('Delivered','Evaluated')
)
GROUP BY h.status, d.status
ORDER BY avg_days DESC;
→ Visualización: Row chart. Guarda como "Avg Days Per Transition"
Q3 — Top Mentors leaderboard
sqlSELECT
  m.full_name,
  m.company,
  COUNT(DISTINCT tm.team_id) AS teams_mentored,
  ROUND(AVG(e.score), 2)     AS avg_score
FROM mentor m
JOIN team_mentor tm ON tm.mentor_id = m.id
JOIN project p      ON p.team_id = tm.team_id
JOIN evaluation e   ON e.project_id = p.id
GROUP BY m.id, m.full_name, m.company
ORDER BY avg_score DESC
LIMIT 10;
→ Visualización: Table. Guarda como "Mentor Leaderboard"

ard:
bash# Exportar la config de Metabase
docker exec hackathon_pg pg_dump -U admin metabase > sql/metabase_backup.sql

docker exec -i hackathon_pg psql -U admin -d metabase < sql/metabase_backup.sql# dexterfinal
