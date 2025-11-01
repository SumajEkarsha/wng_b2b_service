-- Critical Performance Indexes for SQLAlchemy Optimization
-- Run this to add missing indexes on foreign keys

-- Students table indexes
CREATE INDEX IF NOT EXISTS idx_students_class_id ON students(class_id);
CREATE INDEX IF NOT EXISTS idx_students_school_id ON students(school_id);

-- Cases table indexes
CREATE INDEX IF NOT EXISTS idx_cases_student_id ON cases(student_id);
CREATE INDEX IF NOT EXISTS idx_cases_assigned_counsellor ON cases(assigned_counsellor);
CREATE INDEX IF NOT EXISTS idx_cases_created_by ON cases(created_by);
CREATE INDEX IF NOT EXISTS idx_cases_status ON cases(status);

-- Student responses indexes
CREATE INDEX IF NOT EXISTS idx_student_responses_student_id ON student_responses(student_id);
CREATE INDEX IF NOT EXISTS idx_student_responses_assessment_id ON student_responses(assessment_id);
CREATE INDEX IF NOT EXISTS idx_student_responses_completed_at ON student_responses(completed_at);

-- Assessments indexes
CREATE INDEX IF NOT EXISTS idx_assessments_school_id ON assessments(school_id);
CREATE INDEX IF NOT EXISTS idx_assessments_class_id ON assessments(class_id);
CREATE INDEX IF NOT EXISTS idx_assessments_template_id ON assessments(template_id);

-- Classes indexes
CREATE INDEX IF NOT EXISTS idx_classes_school_id ON classes(school_id);
CREATE INDEX IF NOT EXISTS idx_classes_teacher_id ON classes(teacher_id);

-- Users indexes
CREATE INDEX IF NOT EXISTS idx_users_school_id ON users(school_id);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Journal entries indexes
CREATE INDEX IF NOT EXISTS idx_journal_entries_case_id ON journal_entries(case_id);
CREATE INDEX IF NOT EXISTS idx_journal_entries_author_id ON journal_entries(author_id);

-- Session notes indexes
CREATE INDEX IF NOT EXISTS idx_session_notes_case_id ON session_notes(case_id);
CREATE INDEX IF NOT EXISTS idx_session_notes_counsellor_id ON session_notes(counsellor_id);

-- Observations indexes
CREATE INDEX IF NOT EXISTS idx_observations_student_id ON observations(student_id);
CREATE INDEX IF NOT EXISTS idx_observations_reporter_id ON observations(reporter_id);

-- Risk alerts indexes
CREATE INDEX IF NOT EXISTS idx_risk_alerts_student_id ON risk_alerts(student_id);
CREATE INDEX IF NOT EXISTS idx_risk_alerts_assigned_to ON risk_alerts(assigned_to);

-- AI recommendations indexes
CREATE INDEX IF NOT EXISTS idx_ai_recommendations_student_id ON ai_recommendations(student_id);
CREATE INDEX IF NOT EXISTS idx_ai_recommendations_case_id ON ai_recommendations(case_id);

-- Calendar events indexes
CREATE INDEX IF NOT EXISTS idx_calendar_events_student_id ON calendar_events(student_id);
CREATE INDEX IF NOT EXISTS idx_calendar_events_case_id ON calendar_events(case_id);
CREATE INDEX IF NOT EXISTS idx_calendar_events_creator_id ON calendar_events(creator_id);

-- Goals indexes
CREATE INDEX IF NOT EXISTS idx_goals_case_id ON goals(case_id);

-- Resources indexes
CREATE INDEX IF NOT EXISTS idx_resources_school_id ON resources(school_id);
CREATE INDEX IF NOT EXISTS idx_resources_author_id ON resources(author_id);

-- Consent records indexes
CREATE INDEX IF NOT EXISTS idx_consent_records_student_id ON consent_records(student_id);

-- Activities indexes
CREATE INDEX IF NOT EXISTS idx_activities_school_id ON activities(school_id);
CREATE INDEX IF NOT EXISTS idx_activities_creator_id ON activities(creator_id);

-- Daily boosters indexes
CREATE INDEX IF NOT EXISTS idx_daily_boosters_school_id ON daily_boosters(school_id);
CREATE INDEX IF NOT EXISTS idx_daily_boosters_creator_id ON daily_boosters(creator_id);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_cases_counsellor_status ON cases(assigned_counsellor, status);
CREATE INDEX IF NOT EXISTS idx_student_responses_student_completed ON student_responses(student_id, completed_at);
CREATE INDEX IF NOT EXISTS idx_users_school_role ON users(school_id, role);
