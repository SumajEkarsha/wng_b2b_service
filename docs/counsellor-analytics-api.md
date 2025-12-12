# Counsellor Analytics API Documentation

Base URL: `/api/v1/analytics/counsellor`

---

## Overview

This API provides comprehensive analytics for counsellors to monitor school-wide, class-wise, and student-wise wellbeing metrics, engagement data, and activity tracking.

---

## Endpoints Summary

| # | Endpoint | Description |
|---|----------|-------------|
| 1 | `GET /overview` | School-wide aggregated analytics |
| 2 | `GET /classes` | Analytics for all classes |
| 3 | `GET /classes/{class_id}` | Detailed analytics for a specific class |
| 4 | `GET /students` | Analytics for all students (paginated) |
| 5 | `GET /students/{student_id}` | Comprehensive analytics for a student |
| 6 | `GET /students/{student_id}/assessments` | Student's assessment history |
| 7 | `GET /students/{student_id}/activities` | Student's activity history |
| 8 | `GET /students/{student_id}/webinars` | Student's webinar attendance |
| 9 | `GET /students/{student_id}/streak` | Student's daily streak details |

---

## 1. School Overview Analytics

```
GET /api/v1/analytics/counsellor/overview
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `school_id` | UUID | Yes | School ID |
| `days` | integer | No | Filter to last N days (default: 30) |

**Response:**
```json
{
  "status": "success",
  "data": {
    "school_id": "uuid",
    "school_name": "ABC School",
    "period": {
      "start_date": "2025-11-11",
      "end_date": "2025-12-11",
      "days": 30
    },
    "summary": {
      "total_students": 177,
      "total_classes": 6,
      "avg_wellbeing_score": 78.5,
      "avg_assessment_completion": 85.2,
      "avg_activity_completion": 72.4,
      "avg_daily_streak": 8.3,
      "total_app_openings": 4520
    },
    "risk_distribution": {
      "low": 126,
      "medium": 34,
      "high": 17
    },
    "engagement": {
      "total_app_openings": 4520,
      "total_assessments_completed": 892,
      "total_activities_completed": 1456
    },
    "top_performers": [
      {
        "student_id": "uuid",
        "student_name": "Ananya Singh",
        "class_name": "Grade 8-A",
        "daily_streak": 20,
        "wellbeing_score": 90
      }
    ],
    "at_risk_students": [
      {
        "student_id": "uuid",
        "student_name": "Rohan Kumar",
        "class_name": "Grade 8-A",
        "wellbeing_score": 45,
        "risk_level": "high",
        "last_active": "2025-12-05"
      }
    ]
  }
}
```

---

## 2. Class List Analytics

```
GET /api/v1/analytics/counsellor/classes
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `school_id` | UUID | Yes | School ID |
| `search` | string | No | Search by class name or teacher |
| `grade` | string | No | Filter by grade (e.g., "8", "9") |
| `days` | integer | No | Filter to last N days (default: 30) |

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_classes": 6,
    "classes": [
      {
        "class_id": "uuid",
        "name": "Grade 8-A",
        "grade": "8",
        "section": "A",
        "teacher_id": "uuid",
        "teacher_name": "Mrs. Sharma",
        "total_students": 32,
        "metrics": {
          "avg_wellbeing": 78,
          "assessment_completion": 85,
          "activity_completion": 72,
          "avg_daily_streak": 9.2
        },
        "risk_distribution": {
          "low": 22,
          "medium": 7,
          "high": 3
        },
        "at_risk_count": 3
      }
    ]
  }
}
```

---

## 3. Single Class Analytics

```
GET /api/v1/analytics/counsellor/classes/{class_id}
```

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `class_id` | UUID | Class ID |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `days` | integer | No | Filter to last N days (default: 30) |

**Response:**
```json
{
  "status": "success",
  "data": {
    "class_id": "uuid",
    "name": "Grade 8-A",
    "grade": "8",
    "section": "A",
    "teacher": {
      "id": "uuid",
      "name": "Mrs. Sharma",
      "email": "sharma@school.com"
    },
    "total_students": 32,
    "metrics": {
      "avg_wellbeing": 78,
      "assessment_completion": 85,
      "activity_completion": 72,
      "avg_daily_streak": 9.2,
      "avg_app_openings": 38,
      "avg_session_time": 11.5
    },
    "risk_distribution": {
      "low": 22,
      "medium": 7,
      "high": 3
    },
    "students": [
      {
        "student_id": "uuid",
        "name": "Aarav Sharma",
        "wellbeing_score": 85,
        "risk_level": "low",
        "daily_streak": 12,
        "assessments_completed": 8,
        "activities_completed": 15,
        "last_active": "2025-12-11"
      }
    ]
  }
}
```

---

## 4. Student List Analytics

```
GET /api/v1/analytics/counsellor/students
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `school_id` | UUID | Yes | School ID |
| `class_id` | UUID | No | Filter by class |
| `search` | string | No | Search by name or email |
| `risk_level` | string | No | Filter: low, medium, high |
| `days` | integer | No | Filter to last N days (default: 30) |
| `page` | integer | No | Page number (default: 1) |
| `limit` | integer | No | Items per page (default: 20, max: 100) |

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_students": 177,
    "page": 1,
    "limit": 20,
    "total_pages": 9,
    "students": [
      {
        "student_id": "uuid",
        "name": "Aarav Sharma",
        "class_id": "uuid",
        "class_name": "Grade 8-A",
        "wellbeing_score": 85,
        "risk_level": "low",
        "daily_streak": 12,
        "max_streak": 25,
        "last_active": "2025-12-11",
        "assessments_completed": 8,
        "activities_completed": 15,
        "activities_total": 18,
        "app_openings": 45
      }
    ]
  }
}
```

---

## 5. Single Student Detailed Analytics

```
GET /api/v1/analytics/counsellor/students/{student_id}
```

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `student_id` | UUID | Student ID |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `days` | integer | No | Filter to last N days (default: 30) |

**Response:**
```json
{
  "status": "success",
  "data": {
    "student_id": "uuid",
    "name": "Aarav Sharma",
    "email": "parent@email.com",
    "class": {
      "id": "uuid",
      "name": "Grade 8-A",
      "grade": "8",
      "section": "A"
    },
    "profile": {
      "date_of_birth": "2012-05-15",
      "gender": "male",
      "parent_contact": "+91-9876543210"
    },
    "current_metrics": {
      "wellbeing_score": 85,
      "risk_level": "low",
      "daily_streak": 12,
      "max_streak": 25,
      "last_active": "2025-12-11T14:30:00Z"
    },
    "engagement": {
      "total_app_openings": 45,
      "avg_session_time": 12,
      "total_time_spent": 540,
      "assessments_completed": 8,
      "assessments_total": 10,
      "activities_completed": 15,
      "activities_total": 18,
      "webinars_attended": 3,
      "webinars_total": 4
    },
    "streak_history": {
      "current_streak": 12,
      "max_streak": 25,
      "weekly_data": [
        { "day": "Mon", "date": "2025-12-09", "app_opened": true, "activity_completed": true },
        { "day": "Tue", "date": "2025-12-10", "app_opened": true, "activity_completed": true }
      ]
    },
    "wellbeing_trend": []
  }
}
```

---

## 6. Student Assessment History

```
GET /api/v1/analytics/counsellor/students/{student_id}/assessments
```

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `student_id` | UUID | Student ID |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `include_responses` | boolean | No | Include question responses (default: false) |
| `days` | integer | No | Filter to last N days |

**Response:**
```json
{
  "status": "success",
  "data": {
    "student_id": "uuid",
    "student_name": "Aarav Sharma",
    "total_assessments": 8,
    "assessments": [
      {
        "assessment_id": "uuid",
        "template_id": "uuid",
        "template_name": "PHQ-9 Depression Screening",
        "category": "depression",
        "completed_at": "2025-12-10T10:30:00Z",
        "total_score": 8,
        "max_score": 45,
        "total_questions": 9,
        "questions_answered": 9,
        "risk_level": "low",
        "responses": [
          {
            "question_id": "q1",
            "question_text": "Little interest or pleasure in doing things?",
            "answer_value": 1,
            "score": 1
          }
        ]
      }
    ]
  }
}
```

---

## 7. Student Activity History

```
GET /api/v1/analytics/counsellor/students/{student_id}/activities
```

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `student_id` | UUID | Student ID |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | PENDING, SUBMITTED, VERIFIED, REJECTED |
| `days` | integer | No | Filter to last N days |

**Response:**
```json
{
  "status": "success",
  "data": {
    "student_id": "uuid",
    "student_name": "Aarav Sharma",
    "total_activities": 15,
    "status_breakdown": {
      "pending": 3,
      "submitted": 2,
      "verified": 9,
      "rejected": 1
    },
    "activities": [
      {
        "submission_id": "uuid",
        "activity_id": "uuid",
        "activity_title": "Mindfulness Breathing",
        "activity_type": "SOCIAL_EMOTIONAL_DEVELOPMENT",
        "assigned_at": "2025-12-08T09:00:00Z",
        "due_date": "2025-12-15T23:59:59Z",
        "submitted_at": "2025-12-11T14:30:00Z",
        "status": "VERIFIED",
        "feedback": "Great job!",
        "file_url": "https://..."
      }
    ]
  }
}
```

---

## 8. Student Webinar History

```
GET /api/v1/analytics/counsellor/students/{student_id}/webinars
```

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `student_id` | UUID | Student ID |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `attended` | boolean | No | Filter by attendance status |
| `days` | integer | No | Filter to last N days |

**Response:**
```json
{
  "status": "success",
  "data": {
    "student_id": "uuid",
    "student_name": "Aarav Sharma",
    "total_webinars": 4,
    "attended_count": 3,
    "missed_count": 1,
    "attendance_rate": 75.0,
    "webinars": [
      {
        "webinar_id": "uuid",
        "title": "Managing Exam Stress",
        "description": "Learn techniques to manage stress",
        "scheduled_at": "2025-12-08T15:00:00Z",
        "duration_minutes": 45,
        "host": { "name": "Dr. Priya Sharma" },
        "attended": true,
        "join_time": "2025-12-08T14:58:00Z",
        "leave_time": "2025-12-08T15:45:00Z",
        "watch_duration_minutes": 47,
        "recording_url": "https://..."
      }
    ]
  }
}
```

---

## 9. Student Daily Streak

```
GET /api/v1/analytics/counsellor/students/{student_id}/streak
```

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `student_id` | UUID | Student ID |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `days` | integer | No | Number of days to return (default: 30) |

**Response:**
```json
{
  "status": "success",
  "data": {
    "student_id": "uuid",
    "student_name": "Aarav Sharma",
    "current_streak": 12,
    "max_streak": 25,
    "total_active_days": 45,
    "streak_start_date": "2025-11-30",
    "daily_history": [
      {
        "date": "2025-12-11",
        "day_of_week": "Thursday",
        "app_opened": true,
        "app_open_time": "2025-12-11T08:30:00Z",
        "activity_completed": true,
        "activities_count": 2,
        "session_duration_minutes": 15,
        "streak_maintained": true
      }
    ],
    "weekly_summary": [
      {
        "week_start": "2025-12-09",
        "week_end": "2025-12-15",
        "days_active": 3,
        "activities_completed": 5,
        "avg_session_time": 13.5
      }
    ]
  }
}
```

---

## Frontend Integration

### TypeScript Types

```typescript
// types/counsellor-analytics.ts

interface SchoolOverview {
  school_id: string;
  school_name: string;
  period: { start_date: string; end_date: string; days: number };
  summary: {
    total_students: number;
    total_classes: number;
    avg_wellbeing_score: number | null;
    avg_assessment_completion: number;
    avg_activity_completion: number;
    avg_daily_streak: number;
    total_app_openings: number;
  };
  risk_distribution: { low: number; medium: number; high: number };
  top_performers: StudentSummary[];
  at_risk_students: AtRiskStudent[];
}

interface ClassAnalytics {
  class_id: string;
  name: string;
  grade: string;
  section: string | null;
  teacher_name: string | null;
  total_students: number;
  metrics: ClassMetrics;
  risk_distribution: { low: number; medium: number; high: number };
  students?: StudentListItem[];
}

interface StudentListItem {
  student_id: string;
  name: string;
  class_name: string | null;
  wellbeing_score: number | null;
  risk_level: 'low' | 'medium' | 'high';
  daily_streak: number;
  max_streak: number;
  last_active: string | null;
  assessments_completed: number;
  activities_completed: number;
}

interface StudentDetailed {
  student_id: string;
  name: string;
  class: { id: string; name: string; grade: string } | null;
  current_metrics: {
    wellbeing_score: number | null;
    risk_level: string;
    daily_streak: number;
    max_streak: number;
  };
  engagement: {
    total_app_openings: number;
    assessments_completed: number;
    activities_completed: number;
  };
  streak_history: {
    current_streak: number;
    weekly_data: DailyStreak[];
  };
}

interface DailyStreak {
  date: string;
  day: string;
  app_opened: boolean;
  activity_completed: boolean;
}
```

### API Client

```typescript
// api/counsellor-analytics.ts

const BASE_URL = '/api/v1/analytics/counsellor';

export const counsellorAnalyticsApi = {
  // School Overview
  getOverview: (schoolId: string, days = 30) =>
    fetch(`${BASE_URL}/overview?school_id=${schoolId}&days=${days}`)
      .then(r => r.json()),

  // Classes
  getClasses: (schoolId: string, params?: { search?: string; grade?: string }) => {
    const query = new URLSearchParams({ school_id: schoolId, ...params }).toString();
    return fetch(`${BASE_URL}/classes?${query}`).then(r => r.json());
  },

  getClass: (classId: string, days = 30) =>
    fetch(`${BASE_URL}/classes/${classId}?days=${days}`).then(r => r.json()),

  // Students
  getStudents: (schoolId: string, params?: {
    class_id?: string;
    search?: string;
    risk_level?: string;
    page?: number;
    limit?: number;
  }) => {
    const query = new URLSearchParams({ school_id: schoolId, ...params as any }).toString();
    return fetch(`${BASE_URL}/students?${query}`).then(r => r.json());
  },

  getStudent: (studentId: string, days = 30) =>
    fetch(`${BASE_URL}/students/${studentId}?days=${days}`).then(r => r.json()),

  getStudentAssessments: (studentId: string, includeResponses = false) =>
    fetch(`${BASE_URL}/students/${studentId}/assessments?include_responses=${includeResponses}`)
      .then(r => r.json()),

  getStudentActivities: (studentId: string, status?: string) => {
    const query = status ? `?status=${status}` : '';
    return fetch(`${BASE_URL}/students/${studentId}/activities${query}`).then(r => r.json());
  },

  getStudentWebinars: (studentId: string) =>
    fetch(`${BASE_URL}/students/${studentId}/webinars`).then(r => r.json()),

  getStudentStreak: (studentId: string, days = 30) =>
    fetch(`${BASE_URL}/students/${studentId}/streak?days=${days}`).then(r => r.json()),
};
```

### React Component Example

```tsx
// components/CounsellorDashboard.tsx
import { useEffect, useState } from 'react';
import { counsellorAnalyticsApi } from '../api/counsellor-analytics';

function CounsellorDashboard({ schoolId }: { schoolId: string }) {
  const [overview, setOverview] = useState<SchoolOverview | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    counsellorAnalyticsApi.getOverview(schoolId)
      .then(res => setOverview(res.data))
      .finally(() => setLoading(false));
  }, [schoolId]);

  if (loading) return <div>Loading...</div>;
  if (!overview) return <div>Error loading data</div>;

  return (
    <div className="dashboard">
      <h1>{overview.school_name} Dashboard</h1>
      
      {/* Summary Cards */}
      <div className="summary-grid">
        <StatCard title="Students" value={overview.summary.total_students} />
        <StatCard title="Avg Wellbeing" value={overview.summary.avg_wellbeing_score} suffix="%" />
        <StatCard title="Activity Completion" value={overview.summary.avg_activity_completion} suffix="%" />
        <StatCard title="Avg Streak" value={overview.summary.avg_daily_streak} suffix=" days" />
      </div>

      {/* Risk Distribution */}
      <div className="risk-chart">
        <h3>Risk Distribution</h3>
        <div className="risk-bars">
          <div className="bar low" style={{ width: `${overview.risk_distribution.low / overview.summary.total_students * 100}%` }}>
            Low: {overview.risk_distribution.low}
          </div>
          <div className="bar medium" style={{ width: `${overview.risk_distribution.medium / overview.summary.total_students * 100}%` }}>
            Medium: {overview.risk_distribution.medium}
          </div>
          <div className="bar high" style={{ width: `${overview.risk_distribution.high / overview.summary.total_students * 100}%` }}>
            High: {overview.risk_distribution.high}
          </div>
        </div>
      </div>

      {/* At-Risk Students Alert */}
      {overview.at_risk_students.length > 0 && (
        <div className="alert-section">
          <h3>⚠️ Students Needing Attention</h3>
          <ul>
            {overview.at_risk_students.map(student => (
              <li key={student.student_id}>
                <strong>{student.student_name}</strong> ({student.class_name})
                - Wellbeing: {student.wellbeing_score}
                - Last Active: {student.last_active || 'Never'}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

---

## Database Tables Required

The following tables are created by the migration:

```sql
-- student_app_sessions: Tracks individual app sessions
-- student_daily_streaks: Tracks daily activity for streak calculation
-- student_streak_summary: Denormalized streak data for performance
-- student_webinar_attendance: Tracks student webinar attendance
```

Run migration:
```bash
alembic upgrade head
```

---

## Error Responses

| Status | Code | Description |
|--------|------|-------------|
| 400 | INVALID_PARAMETERS | Invalid query parameters |
| 404 | NOT_FOUND | Resource not found |
| 500 | INTERNAL_ERROR | Server error |

```json
{
  "detail": "Student not found"
}
```
