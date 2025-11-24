-- Drop existing enum types that are causing conflicts
-- Run this in NeonDB SQL Editor for the webinars-migration branch

DROP TYPE IF EXISTS webinarcategory CASCADE;
DROP TYPE IF EXISTS webinarstatus CASCADE;
DROP TYPE IF EXISTS webinarlevel CASCADE;
DROP TYPE IF EXISTS registrationstatus CASCADE;
DROP TYPE IF EXISTS availabilitystatus CASCADE;
DROP TYPE IF EXISTS bookingstatus CASCADE;

-- After running this, execute: alembic upgrade head
