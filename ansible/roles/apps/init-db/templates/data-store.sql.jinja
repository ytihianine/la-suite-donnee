-- Wrapping to handle exceptions (e.g., if roles or users already exist)
DO $$
BEGIN

-- =================
-- Roles (NOLOGIN)
-- =================
-- (none)


-- =================
-- Users (LOGIN)
-- =================
CREATE ROLE analyst_superset LOGIN PASSWORD 'analyst_password';
COMMENT ON ROLE analyst_superset IS 'Utilisateur analyste pour accéder à la base de données métier';
GRANT pg_read_all_data TO analyst_superset;

CREATE ROLE airflow_task_writer LOGIN PASSWORD 'analyst_password';
COMMENT ON ROLE airflow_task_writer IS 'Utilisateur analyste pour accéder à la base de données métier';
GRANT pg_read_all_data TO airflow_task_writer;
GRANT pg_write_all_data TO airflow_task_writer;
GRANT pg_maintain TO airflow_task_writer;
GRANT pg_monitor TO airflow_task_writer;

EXCEPTION WHEN duplicate_object THEN RAISE NOTICE '%, skipping', SQLERRM USING ERRCODE = SQLSTATE;
END
$$;
