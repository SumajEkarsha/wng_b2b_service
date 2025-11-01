-- Performance Optimization: Add Database Indexes
-- Run this script to improve query performance

-- Students table indexes
CREATE INDEX IF NOT EXISTS idx_students_school_id ON students(school_id);
CREATE INDEX IF NOT EXISTS idx_students_grade ON students(grade);
CREATE INDEX IF NOT EXISTS idx_students_class_id ON students(class_id);
CREATE INDEX IF NOT EXISTS idx_students_created_at ON students(created_at);

-- Cases table indexes
CREATE INDEX IF NOT EXISTS idx_cases_school_id ON cases(school_id);
CREATE INDEX IF NOT EXISTS idx_cases_student_id ON cases(student_id);
CREATE INDEX IF NOT EXISTS idx_cases_counsellor_id ON cases(assigned_counsellor_id);
CREATE INDEX IF NOT EXISTS idx_cases_risk_level ON cases(risk_level);
CREATE INDEX IF NOT EXISTS idx_cases_status ON cases(status);
CREATE INDEX IF NOT EXISTS idx_cases_created_at ON cases(created_at);
CREATE INDEX IF NOT EXISTS idx_cases_updated_at ON cases(updated_at);

-- Composite index for common queries
CREATE INDEX IF NOT EXISTS idx_cases_school_status_risk ON cases(school_id, status, risk_level);

-- Assessments table indexes
CREATE INDEX IF NOT EXISTS idx_assessments_school_id ON assessments(school_id);
CREATE INDEX IF NOT EXISTS idx_assessments_student_id ON assessments(student_id);
CREATE INDEX IF NOT EXISTS idx_assessments_date ON assessments(assessment_date);
CREATE INDEX IF NOT EXISTS idx_assessments_created_at ON assessments(created_at);

-- Resources table indexes
CREATE INDEX IF NOT EXISTS idx_resources_school_id ON resources(school_id);
CREATE INDEX IF NOT EXISTS idx_resources_category ON resources(category);
CREATE INDEX IF NOT EXISTS idx_resources_type ON resources(type);
CREATE INDEX IF NOT EXISTS idx_resources_status ON resources(status);
CREATE INDEX IF NOT EXISTS idx_resources_created_at ON resources(created_at);

-- Classes table indexes
CREATE INDEX IF NOT EXISTS idx_classes_school_id ON classes(school_id);
CREATE INDEX IF NOT EXISTS idx_classes_grade ON classes(grade);
CREATE INDEX IF NOT EXISTS idx_classes_teacher_id ON classes(teacher_id);

-- Users table indexes
CREATE INDEX IF NOT EXISTS idx_users_school_id ON users(school_id);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Session notes indexes
CREATE INDEX IF NOT EXISTS idx_session_notes_case_id ON session_notes(case_id);
CREATE INDEX IF NOT EXISTS idx_session_notes_created_at ON session_notes(created_at);

-- Goals indexes
CREATE INDEX IF NOT EXISTS idx_goals_case_id ON goals(case_id);
CREATE INDEX IF NOT EXISTS idx_goals_status ON goals(status);

-- Observations indexes
CREATE INDEX IF NOT EXISTS idx_observations_student_id ON observations(student_id);
CREATE INDEX IF NOT EXISTS idx_observations_created_at ON observations(created_at);

-- Calendar events indexes
CREATE INDEX IF NOT EXISTS idx_calendar_events_user_id ON calendar_events(user_id);
CREATE INDEX IF NOT EXISTS idx_calendar_events_date ON calendar_events(event_date);
CREATE INDEX IF NOT EXISTS idx_calendar_events_type ON calendar_events(event_type);

-- Activities indexes
CREATE INDEX IF NOT EXISTS idx_activities_school_id ON activities(school_id);
CREATE INDEX IF NOT EXISTS idx_activities_created_by ON activities(created_by);
CREATE INDEX IF NOT EXISTS idx_activities_date ON activities(activity_date);

-- Webinars indexes
CREATE INDEX IF NOT EXISTS idx_webinars_school_id ON webinars(school_id);
CREATE INDEX IF NOT EXISTS idx_webinars_date ON webinars(webinar_date);
CREATE INDEX IF NOT EXISTS idx_webinars_status ON webinars(status);

-- Analyze tables after creating indexes
ANALYZE students;
ANALYZE cases;
ANALYZE assessments;
ANALYZE resources;
ANALYZE classes;
ANALYZE users;
ANALYZE session_notes;
ANALYZE goals;
ANALYZE observations;
ANALYZE calendar_events;
ANALYZE activities;
ANALYZE webinars;

-- Verify indexes were created
SELECT 
    tablename,
    indexname,
    indexdef
FROM 
    pg_indexes
WHERE 
    schemaname = 'public'
    AND indexname LIKE 'idx_%'
ORDER BY 
    tablename, indexname;
