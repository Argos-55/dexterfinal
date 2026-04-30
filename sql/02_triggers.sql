-- ============================================================
-- TRIGGER 1: Max participantes por equipo
-- ============================================================
CREATE OR REPLACE FUNCTION check_team_capacity()
RETURNS TRIGGER AS $$
DECLARE
  v_current_count INTEGER;
  v_max_size      INTEGER;
BEGIN
  SELECT COUNT(*) INTO v_current_count
  FROM team_participant
  WHERE team_id = NEW.team_id;

  SELECT h.max_team_size INTO v_max_size
  FROM hackathon h
  JOIN team t ON t.hackathon_id = h.id
  WHERE t.id = NEW.team_id;

  IF v_current_count >= v_max_size THEN
    RAISE EXCEPTION
      'Team % has reached its maximum capacity of % participants.',
      NEW.team_id, v_max_size
    USING ERRCODE = 'check_violation';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_team_capacity
BEFORE INSERT ON team_participant
FOR EACH ROW EXECUTE FUNCTION check_team_capacity();

-- ============================================================
-- TRIGGER 2: Max equipos por mentor
-- ============================================================
CREATE OR REPLACE FUNCTION check_mentor_capacity()
RETURNS TRIGGER AS $$
DECLARE
  v_assigned_count INTEGER;
  v_max_teams      INTEGER;
BEGIN
  SELECT COUNT(*) INTO v_assigned_count
  FROM team_mentor
  WHERE mentor_id = NEW.mentor_id;

  SELECT max_teams INTO v_max_teams
  FROM mentor
  WHERE id = NEW.mentor_id;

  IF v_assigned_count >= v_max_teams THEN
    RAISE EXCEPTION
      'Mentor % has reached their maximum capacity of % teams.',
      NEW.mentor_id, v_max_teams
    USING ERRCODE = 'check_violation';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_mentor_capacity
BEFORE INSERT ON team_mentor
FOR EACH ROW EXECUTE FUNCTION check_mentor_capacity();

-- ============================================================
-- TRIGGER 3: Auto-log en project_status_history en UPDATE
-- ============================================================
CREATE OR REPLACE FUNCTION log_project_status_change()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.current_status IS DISTINCT FROM OLD.current_status THEN
    INSERT INTO project_status_history (project_id, status, changed_at, changed_by)
    VALUES (NEW.id, NEW.current_status, NOW(), current_user);
  END IF;
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_project_status_history
BEFORE UPDATE ON project
FOR EACH ROW EXECUTE FUNCTION log_project_status_change();

-- ============================================================
-- TRIGGER 4: Registrar status inicial en INSERT
-- ============================================================
CREATE OR REPLACE FUNCTION log_initial_project_status()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO project_status_history (project_id, status, changed_at, changed_by)
  VALUES (NEW.id, NEW.current_status, NOW(), current_user);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_project_initial_status
AFTER INSERT ON project
FOR EACH ROW EXECUTE FUNCTION log_initial_project_status();
