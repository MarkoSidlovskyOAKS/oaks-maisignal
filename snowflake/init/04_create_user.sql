-- Create service account user and role for MAiSIGNAL.
-- Replace <strong_password> with a secure password before executing.

CREATE ROLE IF NOT EXISTS maisignal_svc_role;

CREATE USER IF NOT EXISTS maisignal_svc
    PASSWORD = '<strong_password>'
    DEFAULT_ROLE = maisignal_svc_role
    DEFAULT_WAREHOUSE = compute_wh
    MUST_CHANGE_PASSWORD = FALSE;

-- Grant database and schema access.
GRANT USAGE ON DATABASE maisignal TO ROLE maisignal_svc_role;
GRANT USAGE ON SCHEMA maisignal.raw TO ROLE maisignal_svc_role;

-- Grant table-level privileges.
GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA maisignal.raw TO ROLE maisignal_svc_role;
GRANT SELECT, INSERT ON FUTURE TABLES IN SCHEMA maisignal.raw TO ROLE maisignal_svc_role;

-- Assign role to user.
GRANT ROLE maisignal_svc_role TO USER maisignal_svc;
