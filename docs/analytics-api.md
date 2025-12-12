# Analytics API Documentation

Base URL: `/api/v1/analytics`

---

## Assessment Analytics

### 1. Get Single Assessment Analytics

```
GET /api/v1/analytics/assessments/{assessment_id}
```

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `assessment_id` | UUID | Assessment ID |

**Response:**
```json
{
  "status": "success",
  "data": {
    "assessment_id": "uuid",
    "template_name": "PHQ-9 Depression Screening",
    "category": "depression",
    "title": "Q1 Screening - Grade 8A",
    "class_name": "Grade 8-A",
    "created_at": "2024-10-24T15:30:00Z",
    "completion_metrics": {
      "total_expected": 30,
      "total_completed": 25,
      "completion_rate": 83.3
    },
    "overall_statistics": {
      "min": 2.0,
      "max": 18.0,
      "mean": 8.5,
      "median": 7.0,
      "std_dev": 3.2,
      "count": 25,
      "percentiles": {
        "25th": 5.0,
        "50th": 7.0,
        "75th": 11.0
      }
    },
    "score_distribution": {
      "low": 10,
      "medium": 12,
      "high": 3
    },
    "question_analysis": [
      {
        "question_id": "q1",
        "question_text": "How often do you feel sad?",
        "response_count": 25,
        "average_score": 2.1,
        "min_score": 0,
        "max_score": 4
      }
    ],
    "student_results": [
      {
        "student_id": "uuid",
        "student_name": "John Doe",
        "total_score": 12.0,
        "completed_at": "2024-10-24T16:00:00Z"
      }
    ]
  }
}
```

---

### 2. Get Student Assessment Analytics

```
GET /api/v1/analytics/students/{student_id}/assessments
```

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `student_id` | UUID | Student ID |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `school_id` | UUID | No | Filter by school |
| `category` | string | No | Filter by category (depression, anxiety, behavioral) |
| `days` | integer | No | Filter to last N days |

**Example:**
```
GET /api/v1/analytics/students/123e4567.../assessments?category=depression&days=30
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "student_id": "uuid",
    "student_name": "John Doe",
    "class_id": "uuid",
    "total_assessments": 5,
    "overall_statistics": {
      "min": 6.0,
      "max": 14.0,
      "mean": 9.2,
      "median": 8.0,
      "std_dev": 2.8,
      "count": 5
    },
    "category_breakdown": [
      {
        "category": "depression",
        "assessment_count": 3,
        "total_responses": 27,
        "average_score": 2.1
      },
      {
        "category": "anxiety",
        "assessment_count": 2,
        "total_responses": 18,
        "average_score": 1.8
      }
    ],
    "score_trend": [
      {
        "date": "2024-09-15T10:00:00Z",
        "assessment": "PHQ-9",
        "score": 12.0
      },
      {
        "date": "2024-10-15T10:00:00Z",
        "assessment": "PHQ-9",
        "score": 8.0
      }
    ],
    "class_comparison": {
      "class_average": 9.5,
      "student_average": 9.2,
      "difference": -0.3,
      "percentile_rank": null
    },
    "assessments": [
      {
        "assessment_id": "uuid",
        "template_name": "PHQ-9",
        "category": "depression",
        "title": "Q1 Screening",
        "total_score": 8.0,
        "completed_at": "2024-10-15T10:00:00Z"
      }
    ]
  }
}
```

---

## Activity Analytics

### 3. Get Single Activity Analytics

```
GET /api/v1/analytics/activities/{activity_id}
```

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `activity_id` | UUID | Activity ID |

**Response:**
```json
{
  "status": "success",
  "data": {
    "activity_id": "uuid",
    "activity_name": "Mindfulness Breathing Exercise",
    "description": "A calming breathing activity...",
    "type": "SOCIAL_EMOTIONAL_DEVELOPMENT",
    "duration": 15,
    "target_grades": ["5", "6", "7"],
    "themes": ["mindfulness", "emotional-regulation", "self-care"],
    "diagnosis": ["Anxiety", "ADHD"],
    "objectives": ["Reduce stress", "Improve focus"],
    "materials": ["Yoga mat", "Timer"],
    "instructions": ["Step 1: Find a quiet space", "Step 2: Sit comfortably"],
    "location": "IN_CLASS",
    "risk_level": "LOW",
    "skill_level": "BEGINNER",
    "thumbnail_url": "https://...",
    "is_counselor_only": false,
    "total_assignments": 4,
    "submission_metrics": {
      "total_expected": 120,
      "total_completed": 95,
      "completion_rate": 79.2,
      "verified_count": 80,
      "pending_review": 15
    },
    "status_distribution": {
      "PENDING": 25,
      "SUBMITTED": 15,
      "VERIFIED": 80,
      "REJECTED": 0
    },
    "class_breakdown": [
      {
        "assignment_id": "uuid",
        "class_id": "uuid",
        "class_name": "Grade 5-A",
        "assigned_at": "2024-10-01T09:00:00Z",
        "due_date": "2024-10-08T23:59:59Z",
        "total_students": 30,
        "completed": 28,
        "completion_rate": 93.3
      }
    ],
    "submission_timeline": [
      { "date": "2024-10-02", "count": 12 },
      { "date": "2024-10-03", "count": 18 },
      { "date": "2024-10-04", "count": 8 }
    ]
  }
}
```

---

### 4. Get Student Activity Analytics

```
GET /api/v1/analytics/students/{student_id}/activities
```

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `student_id` | UUID | Student ID |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `class_id` | UUID | No | Filter by class |
| `status` | string | No | PENDING, SUBMITTED, VERIFIED, REJECTED |
| `days` | integer | No | Filter to last N days |

**Example:**
```
GET /api/v1/analytics/students/123e4567.../activities?status=VERIFIED&days=30
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "student_id": "uuid",
    "student_name": "John Doe",
    "class_id": "uuid",
    "overall_metrics": {
      "total_assigned": 15,
      "total_completed": 12,
      "completion_rate": 80.0,
      "verified_count": 10,
      "rejected_count": 1,
      "pending_count": 3
    },
    "status_distribution": {
      "PENDING": 3,
      "SUBMITTED": 1,
      "VERIFIED": 10,
      "REJECTED": 1
    },
    "activity_type_distribution": [
      { "type": "SOCIAL_EMOTIONAL_DEVELOPMENT", "count": 8, "percentage": 53.3 },
      { "type": "COGNITIVE_DEVELOPMENT", "count": 4, "percentage": 26.7 },
      { "type": "PHYSICAL_DEVELOPMENT", "count": 3, "percentage": 20.0 }
    ],
    "theme_distribution": [
      { "theme": "mindfulness", "count": 5 },
      { "theme": "emotional-regulation", "count": 4 },
      { "theme": "social-skills", "count": 3 }
    ],
    "weekly_completion_trend": [
      { "week_of": "2024-10-07", "completed": 3 },
      { "week_of": "2024-10-14", "completed": 5 },
      { "week_of": "2024-10-21", "completed": 4 }
    ],
    "recent_submissions": [
      {
        "submission_id": "uuid",
        "activity": {
          "activity_id": "uuid",
          "activity_name": "Mindfulness Exercise",
          "description": "A calming breathing activity",
          "type": "SOCIAL_EMOTIONAL_DEVELOPMENT",
          "duration": 15,
          "themes": ["mindfulness", "self-care"],
          "diagnosis": ["Anxiety"],
          "objectives": ["Reduce stress"],
          "location": "IN_CLASS",
          "risk_level": "LOW",
          "skill_level": "BEGINNER",
          "thumbnail_url": "https://..."
        },
        "status": "VERIFIED",
        "submitted_at": "2024-10-20T14:30:00Z",
        "feedback": "Great job!",
        "due_date": "2024-10-21T23:59:59Z",
        "assigned_at": "2024-10-15T09:00:00Z"
      }
    ]
  }
}
```

---

## Combined Analytics

### 5. Get Student Summary (Dashboard)

```
GET /api/v1/analytics/students/{student_id}/summary
```

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `student_id` | UUID | Student ID |

**Response:**
```json
{
  "status": "success",
  "data": {
    "student_id": "uuid",
    "student_name": "John Doe",
    "class_id": "uuid",
    "risk_level": "LOW",
    "wellbeing_score": 75,
    "assessments": {
      "total_completed": 5,
      "average_score": 9.2,
      "last_assessment": "2024-10-15T10:00:00Z"
    },
    "activities": {
      "total_assigned": 15,
      "total_completed": 12,
      "completion_rate": 80.0,
      "status_breakdown": {
        "PENDING": 3,
        "SUBMITTED": 1,
        "VERIFIED": 10,
        "REJECTED": 1
      }
    }
  }
}
```

---

## Frontend Integration Examples

### React/TypeScript

```typescript
// types.ts

// Activity Types (matching fetch API format)
type ActivityType = 'PHYSICAL_DEVELOPMENT' | 'COGNITIVE_DEVELOPMENT' | 
  'SOCIAL_EMOTIONAL_DEVELOPMENT' | 'LANGUAGE_COMMUNICATION_DEVELOPMENT';
type LocationType = 'IN_CLASS' | 'AT_HOME' | 'OTHER';
type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH';
type SkillLevel = 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED';
type SubmissionStatus = 'PENDING' | 'SUBMITTED' | 'VERIFIED' | 'REJECTED';

interface ActivityInfo {
  activity_id: string;
  activity_name: string;
  description: string | null;
  type: ActivityType | null;
  duration: number | null;
  target_grades: string[] | null;
  themes: string[] | null;
  diagnosis: string[] | null;
  objectives: string[] | null;
  materials: string[] | null;
  instructions: string[] | null;
  location: LocationType | null;
  risk_level: RiskLevel | null;
  skill_level: SkillLevel | null;
  thumbnail_url: string | null;
  is_counselor_only: boolean;
}

interface ActivityAnalytics extends ActivityInfo {
  total_assignments: number;
  submission_metrics: {
    total_expected: number;
    total_completed: number;
    completion_rate: number;
    verified_count: number;
    pending_review: number;
  } | null;
  status_distribution: Record<SubmissionStatus, number>;
  class_breakdown: Array<{
    assignment_id: string;
    class_id: string;
    class_name: string | null;
    assigned_at: string;
    due_date: string | null;
    total_students: number;
    completed: number;
    completion_rate: number;
  }>;
  submission_timeline: Array<{ date: string; count: number }>;
}

interface AssessmentAnalytics {
  assessment_id: string;
  template_name: string;
  category: string;
  completion_metrics: {
    total_expected: number;
    total_completed: number;
    completion_rate: number;
  };
  overall_statistics: {
    min: number;
    max: number;
    mean: number;
    median: number;
    std_dev: number;
    count: number;
    percentiles: { "25th": number; "50th": number; "75th": number };
  };
  score_distribution: { low: number; medium: number; high: number };
  question_analysis: Array<{
    question_id: string;
    question_text: string;
    average_score: number;
  }>;
  student_results: Array<{
    student_id: string;
    student_name: string;
    total_score: number;
    completed_at: string;
  }>;
}

interface StudentActivitySubmission {
  submission_id: string;
  activity: ActivityInfo;
  status: SubmissionStatus;
  submitted_at: string | null;
  feedback: string | null;
  due_date: string | null;
  assigned_at: string | null;
}

interface StudentActivityAnalytics {
  student_id: string;
  student_name: string;
  class_id: string | null;
  overall_metrics: {
    total_assigned: number;
    total_completed: number;
    completion_rate: number;
    verified_count: number;
    rejected_count: number;
    pending_count: number;
  };
  status_distribution: Record<SubmissionStatus, number>;
  activity_type_distribution: Array<{
    type: string;
    count: number;
    percentage: number;
  }>;
  theme_distribution: Array<{ theme: string; count: number }>;
  weekly_completion_trend: Array<{ week_of: string; completed: number }>;
  recent_submissions: StudentActivitySubmission[];
}
```

```typescript
// api.ts
const API_BASE = '/api/v1/analytics';

export const analyticsApi = {
  // Assessment Analytics
  getAssessmentAnalytics: (assessmentId: string) =>
    fetch(`${API_BASE}/assessments/${assessmentId}`).then(r => r.json()),

  getStudentAssessments: (studentId: string, params?: { category?: string; days?: number }) => {
    const query = new URLSearchParams(params as any).toString();
    return fetch(`${API_BASE}/students/${studentId}/assessments?${query}`).then(r => r.json());
  },

  // Activity Analytics
  getActivityAnalytics: (activityId: string) =>
    fetch(`${API_BASE}/activities/${activityId}`).then(r => r.json()),

  getStudentActivities: (studentId: string, params?: { status?: string; days?: number }) => {
    const query = new URLSearchParams(params as any).toString();
    return fetch(`${API_BASE}/students/${studentId}/activities?${query}`).then(r => r.json());
  },

  // Summary
  getStudentSummary: (studentId: string) =>
    fetch(`${API_BASE}/students/${studentId}/summary`).then(r => r.json()),
};
```

```tsx
// StudentDashboard.tsx
import { useEffect, useState } from 'react';
import { analyticsApi } from './api';

function StudentDashboard({ studentId }: { studentId: string }) {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    analyticsApi.getStudentSummary(studentId)
      .then(res => setSummary(res.data));
  }, [studentId]);

  if (!summary) return <div>Loading...</div>;

  return (
    <div>
      <h1>{summary.student_name}</h1>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Assessments</h3>
          <p>Completed: {summary.assessments.total_completed}</p>
          <p>Avg Score: {summary.assessments.average_score}</p>
        </div>
        <div className="stat-card">
          <h3>Activities</h3>
          <p>Completion: {summary.activities.completion_rate}%</p>
          <p>Verified: {summary.activities.status_breakdown.VERIFIED}</p>
        </div>
      </div>
    </div>
  );
}
```

---

## Error Responses

```json
{
  "detail": "Assessment not found"
}
```

| Status Code | Description |
|-------------|-------------|
| 400 | Invalid parameters (e.g., invalid status value) |
| 404 | Resource not found |
| 500 | Server error |


---

## Assessment Monitoring

These endpoints help track assessment completion status and identify response inconsistencies.

### 6. Assessment Monitoring (Completion Tracking)

```
GET /api/v1/analytics/assessments/{assessment_id}/monitoring
```

**Purpose:** Monitor which students have completed, partially completed, or not started an assessment.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `assessment_id` | UUID | Assessment ID |

**Response:**
```json
{
  "status": "success",
  "data": {
    "assessment_id": "uuid",
    "template_name": "PHQ-9 Depression Screening",
    "title": "Q1 Screening - Grade 8A",
    "class_name": "Grade 8-A",
    "total_questions": 9,
    "question_ids": ["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9"],
    "summary": {
      "expected_students": 30,
      "completed": 22,
      "incomplete": 5,
      "not_started": 3,
      "unexpected_responses": 0,
      "completion_rate": 73.3
    },
    "completed_students": [
      {
        "student_id": "uuid",
        "student_name": "John Doe",
        "expected_questions": 9,
        "answered_questions": 9,
        "missing_questions": [],
        "extra_questions": [],
        "completed_at": "2024-10-24T16:00:00Z",
        "total_score": 12.0
      }
    ],
    "incomplete_students": [
      {
        "student_id": "uuid",
        "student_name": "Jane Smith",
        "expected_questions": 9,
        "answered_questions": 6,
        "missing_questions": ["q7", "q8", "q9"],
        "extra_questions": [],
        "completed_at": "2024-10-24T15:30:00Z",
        "total_score": 8.0
      }
    ],
    "not_started_students": [
      {
        "student_id": "uuid",
        "student_name": "Bob Wilson"
      }
    ],
    "unexpected_students": []
  }
}
```

**Use Cases:**
- Dashboard showing assessment completion progress
- Identifying students who need follow-up
- Detecting data quality issues (incomplete responses)

---

### 7. Question-by-Question Breakdown

```
GET /api/v1/analytics/assessments/{assessment_id}/question-breakdown
```

**Purpose:** See detailed response data for each question, including which students answered and their scores.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `assessment_id` | UUID | Assessment ID |

**Response:**
```json
{
  "status": "success",
  "data": {
    "assessment_id": "uuid",
    "template_name": "PHQ-9 Depression Screening",
    "title": "Q1 Screening",
    "total_questions": 9,
    "question_breakdown": [
      {
        "question_id": "q1",
        "question_text": "Little interest or pleasure in doing things?",
        "question_type": "rating_scale",
        "response_count": 25,
        "average_score": 1.8,
        "min_score": 0,
        "max_score": 3,
        "responses": [
          {
            "student_id": "uuid",
            "student_name": "John Doe",
            "answer": 2,
            "score": 2.0
          },
          {
            "student_id": "uuid",
            "student_name": "Jane Smith",
            "answer": 1,
            "score": 1.0
          }
        ]
      },
      {
        "question_id": "q2",
        "question_text": "Feeling down, depressed, or hopeless?",
        "question_type": "rating_scale",
        "response_count": 24,
        "average_score": 2.1,
        "min_score": 0,
        "max_score": 3,
        "responses": [...]
      }
    ]
  }
}
```

**Use Cases:**
- Identifying problematic questions (low response rates)
- Analyzing score patterns per question
- Debugging why students have different response counts

---

### 8. Student Assessment History

```
GET /api/v1/analytics/students/{student_id}/assessment-history
```

**Purpose:** Get complete assessment history for a student, showing completion status for each.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `student_id` | UUID | Student ID |

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `include_responses` | boolean | No | Include individual question responses (default: false) |

**Example:**
```
GET /api/v1/analytics/students/123e4567.../assessment-history?include_responses=true
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "student_id": "uuid",
    "student_name": "John Doe",
    "total_assessments": 5,
    "complete_assessments": 4,
    "incomplete_assessments": 1,
    "assessment_history": [
      {
        "assessment_id": "uuid",
        "template_name": "PHQ-9 Depression Screening",
        "category": "depression",
        "title": "Q1 Screening",
        "total_questions_in_template": 9,
        "questions_answered": 9,
        "total_score": 12.0,
        "completed_at": "2024-10-24T16:00:00Z",
        "is_complete": true,
        "responses": [
          {
            "question_id": "q1",
            "question_text": "Little interest or pleasure?",
            "answer": 2,
            "score": 2.0
          }
        ]
      },
      {
        "assessment_id": "uuid",
        "template_name": "GAD-7 Anxiety",
        "category": "anxiety",
        "title": "Anxiety Check",
        "total_questions_in_template": 7,
        "questions_answered": 5,
        "total_score": 8.0,
        "completed_at": "2024-10-20T14:00:00Z",
        "is_complete": false,
        "responses": [...]
      }
    ]
  }
}
```

---

## Why Responses Differ Between Students

The assessment system allows partial submissions, which means:

1. **Students can submit any subset of questions** - The `/assessments/submit` endpoint doesn't enforce all questions must be answered
2. **No validation against template** - Submissions are accepted even if some questions are missing
3. **Re-submissions overwrite** - If a student re-submits, previous responses are deleted

### Detecting Inconsistencies

Use the monitoring endpoint to identify:
- `incomplete_students` - Students who answered fewer questions than expected
- `missing_questions` - Specific questions each student didn't answer
- `extra_questions` - Questions answered that aren't in the template (data integrity issue)

### Frontend Integration for Monitoring

```typescript
// types.ts
interface AssessmentMonitoring {
  assessment_id: string;
  template_name: string;
  total_questions: number;
  summary: {
    expected_students: number;
    completed: number;
    incomplete: number;
    not_started: number;
    completion_rate: number;
  };
  completed_students: StudentCompletion[];
  incomplete_students: StudentCompletion[];
  not_started_students: { student_id: string; student_name: string }[];
}

interface StudentCompletion {
  student_id: string;
  student_name: string;
  expected_questions: number;
  answered_questions: number;
  missing_questions: string[];
  total_score: number;
  completed_at: string;
  is_complete: boolean;
}
```

```typescript
// api.ts
export const monitoringApi = {
  getAssessmentMonitoring: (assessmentId: string) =>
    fetch(`/api/v1/analytics/assessments/${assessmentId}/monitoring`).then(r => r.json()),

  getQuestionBreakdown: (assessmentId: string) =>
    fetch(`/api/v1/analytics/assessments/${assessmentId}/question-breakdown`).then(r => r.json()),

  getStudentHistory: (studentId: string, includeResponses = false) =>
    fetch(`/api/v1/analytics/students/${studentId}/assessment-history?include_responses=${includeResponses}`)
      .then(r => r.json()),
};
```

```tsx
// AssessmentMonitoringDashboard.tsx
function AssessmentMonitoringDashboard({ assessmentId }: { assessmentId: string }) {
  const [data, setData] = useState<AssessmentMonitoring | null>(null);

  useEffect(() => {
    monitoringApi.getAssessmentMonitoring(assessmentId)
      .then(res => setData(res.data));
  }, [assessmentId]);

  if (!data) return <div>Loading...</div>;

  return (
    <div>
      <h2>{data.template_name}</h2>
      
      {/* Progress Bar */}
      <div className="progress-section">
        <div className="progress-bar" style={{ width: `${data.summary.completion_rate}%` }} />
        <span>{data.summary.completion_rate}% Complete</span>
      </div>

      {/* Summary Cards */}
      <div className="summary-grid">
        <div className="card success">
          <h3>Completed</h3>
          <p>{data.summary.completed}</p>
        </div>
        <div className="card warning">
          <h3>Incomplete</h3>
          <p>{data.summary.incomplete}</p>
        </div>
        <div className="card danger">
          <h3>Not Started</h3>
          <p>{data.summary.not_started}</p>
        </div>
      </div>

      {/* Incomplete Students Alert */}
      {data.incomplete_students.length > 0 && (
        <div className="alert warning">
          <h4>Students with Incomplete Responses</h4>
          <ul>
            {data.incomplete_students.map(s => (
              <li key={s.student_id}>
                {s.student_name} - {s.answered_questions}/{s.expected_questions} questions
                <span className="missing">Missing: {s.missing_questions.join(', ')}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```
