-- ============================================================
-- HACKATHON MANAGEMENT PLATFORM - DDL
-- Normalizado hasta 3NF
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TYPE project_status AS ENUM (
  'Idea', 'Approved', 'In Development', 'Delivered', 'Evaluated'
);

CREATE TABLE hackathon (
  id             SERIAL PRIMARY KEY,
  name           VARCHAR(200) NOT NULL UNIQUE,
  edition        INTEGER NOT NULL DEFAULT 1,
  start_date     DATE NOT NULL,
  end_date       DATE NOT NULL,
  location       VARCHAR(200),
  max_team_size  INTEGER NOT NULL DEFAULT 5 CHECK (max_team_size BETWEEN 2 AND 10),
  created_at     TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT chk_dates CHECK (end_date > start_date)
);

CREATE TABLE track (
  id           SERIAL PRIMARY KEY,
  hackathon_id INTEGER NOT NULL REFERENCES hackathon(id) ON DELETE CASCADE,
  name         VARCHAR(100) NOT NULL,
  description  TEXT,
  UNIQUE (hackathon_id, name)
);

CREATE TABLE participant (
  id            SERIAL PRIMARY KEY,
  hackathon_id  INTEGER NOT NULL REFERENCES hackathon(id),
  full_name     VARCHAR(200) NOT NULL,
  email         VARCHAR(200) NOT NULL,
  skills        TEXT[],
  university    VARCHAR(200),
  country       VARCHAR(100),
  registered_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (hackathon_id, email)
);

CREATE TABLE team (
  id           SERIAL PRIMARY KEY,
  hackathon_id INTEGER NOT NULL REFERENCES hackathon(id),
  track_id     INTEGER NOT NULL REFERENCES track(id),
  name         VARCHAR(200) NOT NULL,
  created_at   TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (hackathon_id, name)
);

CREATE TABLE team_participant (
  team_id        INTEGER NOT NULL REFERENCES team(id) ON DELETE CASCADE,
  participant_id INTEGER NOT NULL REFERENCES participant(id),
  role           VARCHAR(50) DEFAULT 'Member',
  joined_at      TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (team_id, participant_id)
);

CREATE TABLE mentor (
  id         SERIAL PRIMARY KEY,
  full_name  VARCHAR(200) NOT NULL,
  email      VARCHAR(200) NOT NULL UNIQUE,
  expertise  TEXT[],
  company    VARCHAR(200),
  max_teams  INTEGER NOT NULL DEFAULT 3 CHECK (max_teams > 0)
);

CREATE TABLE team_mentor (
  team_id     INTEGER NOT NULL REFERENCES team(id) ON DELETE CASCADE,
  mentor_id   INTEGER NOT NULL REFERENCES mentor(id),
  assigned_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (team_id, mentor_id)
);

CREATE TABLE project (
  id             SERIAL PRIMARY KEY,
  team_id        INTEGER NOT NULL UNIQUE REFERENCES team(id),
  title          VARCHAR(300) NOT NULL,
  description    TEXT,
  repo_url       VARCHAR(500),
  current_status project_status NOT NULL DEFAULT 'Idea',
  created_at     TIMESTAMPTZ DEFAULT NOW(),
  updated_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE project_status_history (
  id           SERIAL PRIMARY KEY,
  project_id   INTEGER NOT NULL REFERENCES project(id) ON DELETE CASCADE,
  status       project_status NOT NULL,
  changed_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  changed_by   VARCHAR(200),
  notes        TEXT
);

CREATE TABLE judge (
  id        SERIAL PRIMARY KEY,
  full_name VARCHAR(200) NOT NULL,
  email     VARCHAR(200) NOT NULL UNIQUE,
  expertise TEXT[]
);

CREATE TABLE evaluation (
  id           SERIAL PRIMARY KEY,
  project_id   INTEGER NOT NULL REFERENCES project(id),
  judge_id     INTEGER NOT NULL REFERENCES judge(id),
  score        NUMERIC(4,2) NOT NULL CHECK (score BETWEEN 0 AND 100),
  feedback     TEXT,
  submitted_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (project_id, judge_id)
);
