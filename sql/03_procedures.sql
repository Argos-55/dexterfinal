-- ============================================================
-- STORED PROCEDURE: SubmitEvaluation
-- Verifica status 'Delivered' antes de insertar evaluacion.
-- Si no -> ROLLBACK automatico via RAISE EXCEPTION.
-- ============================================================
CREATE OR REPLACE PROCEDURE SubmitEvaluation(
  p_judge_id  INTEGER,
  p_team_id   INTEGER,
  p_score     NUMERIC(4,2),
  p_feedback  TEXT DEFAULT NULL
)
LANGUAGE plpgsql AS $$
DECLARE
  v_project_id     INTEGER;
  v_project_status project_status;
BEGIN
  SELECT id, current_status
  INTO v_project_id, v_project_status
  FROM project
  WHERE team_id = p_team_id;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'No project found for team_id = %', p_team_id
    USING ERRCODE = 'no_data_found';
  END IF;

  IF v_project_status <> 'Delivered' THEN
    RAISE EXCEPTION
      'Cannot evaluate project %. Current status: "%" - must be "Delivered".',
      v_project_id, v_project_status
    USING ERRCODE = 'invalid_parameter_value';
  END IF;

  INSERT INTO evaluation (project_id, judge_id, score, feedback)
  VALUES (v_project_id, p_judge_id, p_score, p_feedback);

  UPDATE project
  SET current_status = 'Evaluated'
  WHERE id = v_project_id;

  RAISE NOTICE 'Evaluation submitted for project %.', v_project_id;
END;
$$;
