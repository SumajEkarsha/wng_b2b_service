# Teacher Analytics API Documentation

## Base URL
```
/api/v1/analytics/teacher
```

---

## Endpoints

### 1. GET `/analytics/teacher/overview`

Get aggregated analytics for all classes assigned to the teacher.

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| teacher_id | UUID | Yes | - | The teacher's user ID |
| days | int | No | 30 | Number of days (7, 30, 90, 365) |

#### Response

```json
{
  "success": true,
  "data": {
    "teacher_id": "553ff583-e1a4-45c2-a6c3-2627ba2f27a7",
    "teacher_name": "John Smith",
    "period": {
      "start_date": "2025-11-12",
      "end_date": "2025-12-12",
      "days": 30
    },
    "summary": {
      "total_students": 120,
      "total_classes": 4,
      "avg_wellbeing_score": 72.5,
      "avg_activity_completion": 68.0,
      "avg_daily_streak": 3.2,
      "total_app_openings": 450
    },
    "risk_distribution": {
      "low": 85,
      "medium": 25,
      "high": 10
    },
    "engagement": {
      "total_app_openings": 450,
      "total_assessments_completed": 180,
      "total_activities_completed": 320
    },
    "top_performers": [
      {
        "student_id": "uuid",
        "student_name": "Alice Johnson",
        "class_name": "Grade 5A",
        "daily_streak": 15,
        "wellbeing_score": 92
      }
    ],
    "at_risk_students": [
      {
        "student_id": "uuid",
        "student_name": "Bob Wilson",
        "class_name": "Grade 5B",
        "wellbeing_score": 35,
        "risk_level": "high",
        "last_active": "2025-12-01T00:00:00Z"
      }
    ]
  }
}
```


---

### 2. GET `/analytics/teacher/classes`

Get list of classes assigned to the teacher with analytics metrics.

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| teacher_id | UUID | Yes | - | The teacher's user ID |
| search | string | No | - | Search by class name |
| days | int | No | 30 | Number of days for analytics |

#### Response

```json
{
  "success": true,
  "data": {
    "total_classes": 4,
    "classes": [
      {
        "class_id": "uuid",
        "name": "Grade 5A",
        "grade": "5",
        "section": "A",
        "total_students": 30,
        "metrics": {
          "avg_wellbeing": 75,
          "assessment_completion": 82,
          "activity_completion": 70,
          "avg_daily_streak": 4.5
        },
        "risk_distribution": {
          "low": 22,
          "medium": 6,
          "high": 2
        },
        "at_risk_count": 2
      }
    ]
  }
}
```

---

### 3. GET `/analytics/teacher/classes/{class_id}`

Get detailed analytics for a specific class including student list.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| class_id | UUID | The class ID |

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| days | int | No | 30 | Number of days for analytics |

#### Response

```json
{
  "success": true,
  "data": {
    "class_id": "uuid",
    "name": "Grade 5A",
    "grade": "5",
    "section": "A",
    "total_students": 30,
    "metrics": {
      "avg_wellbeing": 75,
      "assessment_completion": 82,
      "activity_completion": 70,
      "avg_daily_streak": 4.5
    },
    "risk_distribution": {
      "low": 22,
      "medium": 6,
      "high": 2
    },
    "at_risk_count": 2,
    "students": [
      {
        "student_id": "uuid",
        "name": "Alice Johnson",
        "wellbeing_score": 85,
        "risk_level": "low",
        "daily_streak": 12,
        "max_streak": 15,
        "last_active": "2025-12-12T00:00:00Z",
        "assessments_completed": 5,
        "activities_completed": 8
      }
    ]
  }
}
```


---

### 4. GET `/analytics/teacher/students`

Get paginated list of all students from the teacher's classes.

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| teacher_id | UUID | Yes | - | The teacher's user ID |
| class_id | UUID | No | - | Filter by specific class |
| search | string | No | - | Search by student name |
| risk_level | string | No | - | Filter: "low", "medium", "high" |
| days | int | No | 30 | Number of days for analytics |
| page | int | No | 1 | Page number |
| limit | int | No | 20 | Items per page (max 100) |

#### Response

```json
{
  "success": true,
  "data": {
    "total_students": 120,
    "page": 1,
    "limit": 20,
    "total_pages": 6,
    "students": [
      {
        "student_id": "uuid",
        "name": "Alice Johnson",
        "class_id": "uuid",
        "class_name": "Grade 5A",
        "wellbeing_score": 85,
        "risk_level": "low",
        "daily_streak": 12,
        "max_streak": 15,
        "last_active": "2025-12-12T00:00:00Z",
        "assessments_completed": 5,
        "activities_completed": 8
      }
    ]
  }
}
```

---

## TypeScript Interfaces

```typescript
// Period info
interface Period {
  start_date: string;
  end_date: string;
  days: number;
}

// Summary metrics
interface TeacherSummary {
  total_students: number;
  total_classes: number;
  avg_wellbeing_score: number | null;
  avg_activity_completion: number;
  avg_daily_streak: number;
  total_app_openings: number;
}

// Risk distribution
interface RiskDistribution {
  low: number;
  medium: number;
  high: number;
}

// Engagement metrics
interface Engagement {
  total_app_openings: number;
  total_assessments_completed: number;
  total_activities_completed: number;
}

// Top performer
interface TopPerformer {
  student_id: string;
  student_name: string;
  class_name: string | null;
  daily_streak: number;
  wellbeing_score: number | null;
}

// At-risk student
interface AtRiskStudent {
  student_id: string;
  student_name: string;
  class_name: string | null;
  wellbeing_score: number | null;
  risk_level: "low" | "medium" | "high";
  last_active: string | null;
}

// Teacher Overview Response
interface TeacherOverviewResponse {
  teacher_id: string;
  teacher_name: string;
  period: Period;
  summary: TeacherSummary;
  risk_distribution: RiskDistribution;
  engagement: Engagement;
  top_performers: TopPerformer[];
  at_risk_students: AtRiskStudent[];
}


// Class metrics
interface ClassMetrics {
  avg_wellbeing: number | null;
  assessment_completion: number;
  activity_completion: number;
  avg_daily_streak: number;
}

// Class item
interface TeacherClass {
  class_id: string;
  name: string;
  grade: string;
  section: string | null;
  total_students: number;
  metrics: ClassMetrics;
  risk_distribution: RiskDistribution;
  at_risk_count: number;
}

// Classes Response
interface TeacherClassesResponse {
  total_classes: number;
  classes: TeacherClass[];
}

// Student item
interface StudentItem {
  student_id: string;
  name: string;
  class_id?: string;
  class_name?: string;
  wellbeing_score: number | null;
  risk_level: "low" | "medium" | "high";
  daily_streak: number;
  max_streak: number;
  last_active: string | null;
  assessments_completed: number;
  activities_completed: number;
}

// Class Details Response
interface ClassDetailsResponse {
  class_id: string;
  name: string;
  grade: string;
  section: string | null;
  total_students: number;
  metrics: ClassMetrics;
  risk_distribution: RiskDistribution;
  at_risk_count: number;
  students: StudentItem[];
}

// Students Response (paginated)
interface TeacherStudentsResponse {
  total_students: number;
  page: number;
  limit: number;
  total_pages: number;
  students: StudentItem[];
}
```

---

## API Service Example

```typescript
const API_BASE = "/api/v1/analytics/teacher";

interface OverviewParams {
  teacher_id: string;
  days?: number;
}

interface ClassesParams {
  teacher_id: string;
  search?: string;
  days?: number;
}

interface StudentsParams {
  teacher_id: string;
  class_id?: string;
  search?: string;
  risk_level?: "low" | "medium" | "high";
  days?: number;
  page?: number;
  limit?: number;
}

export const teacherAnalyticsApi = {
  async getOverview(params: OverviewParams): Promise<TeacherOverviewResponse> {
    const query = new URLSearchParams();
    query.append("teacher_id", params.teacher_id);
    if (params.days) query.append("days", params.days.toString());
    
    const response = await fetch(`${API_BASE}/overview?${query}`);
    if (!response.ok) throw new Error("Failed to fetch overview");
    const json = await response.json();
    return json.data;
  },

  async getClasses(params: ClassesParams): Promise<TeacherClassesResponse> {
    const query = new URLSearchParams();
    query.append("teacher_id", params.teacher_id);
    if (params.search) query.append("search", params.search);
    if (params.days) query.append("days", params.days.toString());
    
    const response = await fetch(`${API_BASE}/classes?${query}`);
    if (!response.ok) throw new Error("Failed to fetch classes");
    const json = await response.json();
    return json.data;
  },

  async getClassDetails(classId: string, days?: number): Promise<ClassDetailsResponse> {
    const query = days ? `?days=${days}` : "";
    const response = await fetch(`${API_BASE}/classes/${classId}${query}`);
    if (!response.ok) throw new Error("Class not found");
    const json = await response.json();
    return json.data;
  },

  async getStudents(params: StudentsParams): Promise<TeacherStudentsResponse> {
    const query = new URLSearchParams();
    query.append("teacher_id", params.teacher_id);
    if (params.class_id) query.append("class_id", params.class_id);
    if (params.search) query.append("search", params.search);
    if (params.risk_level) query.append("risk_level", params.risk_level);
    if (params.days) query.append("days", params.days.toString());
    if (params.page) query.append("page", params.page.toString());
    if (params.limit) query.append("limit", params.limit.toString());
    
    const response = await fetch(`${API_BASE}/students?${query}`);
    if (!response.ok) throw new Error("Failed to fetch students");
    const json = await response.json();
    return json.data;
  }
};
```


---

## React Query Hooks Example

```typescript
import { useQuery } from "@tanstack/react-query";
import { teacherAnalyticsApi } from "./teacherAnalytics";

export function useTeacherOverview(teacherId: string, days = 30) {
  return useQuery({
    queryKey: ["teacher-overview", teacherId, days],
    queryFn: () => teacherAnalyticsApi.getOverview({ teacher_id: teacherId, days }),
    enabled: !!teacherId,
  });
}

export function useTeacherClasses(teacherId: string, search?: string, days = 30) {
  return useQuery({
    queryKey: ["teacher-classes", teacherId, search, days],
    queryFn: () => teacherAnalyticsApi.getClasses({ teacher_id: teacherId, search, days }),
    enabled: !!teacherId,
  });
}

export function useClassDetails(classId: string, days = 30) {
  return useQuery({
    queryKey: ["class-details", classId, days],
    queryFn: () => teacherAnalyticsApi.getClassDetails(classId, days),
    enabled: !!classId,
  });
}

export function useTeacherStudents(params: StudentsParams) {
  return useQuery({
    queryKey: ["teacher-students", params],
    queryFn: () => teacherAnalyticsApi.getStudents(params),
    enabled: !!params.teacher_id,
  });
}
```

---

## Error Responses

### 404 Not Found
```json
{
  "detail": "Teacher not found"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied. Teacher is not assigned to this class."
}
```

---

---

### 5. GET `/analytics/teacher/students/{student_id}/activities`

Get activity history for a specific student.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| student_id | UUID | The student ID |

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| status | string | No | - | Filter: "PENDING", "SUBMITTED", "VERIFIED", "REJECTED" |
| days | int | No | - | Filter to last N days |

#### Response

```json
{
  "success": true,
  "data": {
    "student_id": "uuid",
    "student_name": "Alice Johnson",
    "total_activities": 15,
    "status_breakdown": {
      "pending": 2,
      "submitted": 5,
      "verified": 7,
      "rejected": 1
    },
    "activities": [
      {
        "submission_id": "uuid",
        "activity_id": "uuid",
        "activity_title": "Mindfulness Exercise",
        "activity_type": "WELLNESS",
        "assigned_at": "2025-12-01T10:00:00Z",
        "due_date": "2025-12-15T23:59:59Z",
        "submitted_at": "2025-12-10T14:30:00Z",
        "status": "VERIFIED",
        "feedback": "Great work!",
        "file_url": "https://..."
      }
    ]
  }
}
```

---

## Additional TypeScript Interfaces

```typescript
// Activity submission
interface ActivitySubmission {
  submission_id: string;
  activity_id: string | null;
  activity_title: string | null;
  activity_type: string | null;
  assigned_at: string | null;
  due_date: string | null;
  submitted_at: string | null;
  status: "PENDING" | "SUBMITTED" | "VERIFIED" | "REJECTED";
  feedback: string | null;
  file_url: string | null;
}

// Status breakdown
interface StatusBreakdown {
  pending: number;
  submitted: number;
  verified: number;
  rejected: number;
}

// Student Activities Response
interface StudentActivitiesResponse {
  student_id: string;
  student_name: string;
  total_activities: number;
  status_breakdown: StatusBreakdown;
  activities: ActivitySubmission[];
}
```

---

## Updated API Service

```typescript
// Add to teacherAnalyticsApi object:

async getStudentActivities(
  studentId: string, 
  params?: { status?: string; days?: number }
): Promise<StudentActivitiesResponse> {
  const query = new URLSearchParams();
  if (params?.status) query.append("status", params.status);
  if (params?.days) query.append("days", params.days.toString());
  
  const queryStr = query.toString() ? `?${query}` : "";
  const response = await fetch(`${API_BASE}/students/${studentId}/activities${queryStr}`);
  if (!response.ok) throw new Error("Failed to fetch student activities");
  const json = await response.json();
  return json.data;
}
```

---

## React Query Hook

```typescript
export function useStudentActivities(
  studentId: string, 
  status?: string, 
  days?: number
) {
  return useQuery({
    queryKey: ["student-activities", studentId, status, days],
    queryFn: () => teacherAnalyticsApi.getStudentActivities(studentId, { status, days }),
    enabled: !!studentId,
  });
}
```

---

### 6. GET `/analytics/teacher/students/{student_id}/assessments`

Get assessment history for a specific student.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| student_id | UUID | The student ID |

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| include_responses | bool | No | false | Include individual question responses |
| days | int | No | - | Filter to last N days |

#### Response

```json
{
  "success": true,
  "data": {
    "student_id": "uuid",
    "student_name": "Alice Johnson",
    "total_assessments": 5,
    "assessments": [
      {
        "assessment_id": "uuid",
        "template_id": "uuid",
        "template_name": "Wellbeing Check",
        "category": "WELLBEING",
        "completed_at": "2025-12-10T14:30:00Z",
        "total_score": 35.0,
        "max_score": 50,
        "total_questions": 10,
        "questions_answered": 10,
        "risk_level": "medium",
        "responses": [
          {
            "question_id": "q1",
            "question_text": "How are you feeling today?",
            "answer_value": 4,
            "score": 4
          }
        ]
      }
    ]
  }
}
```

---

### 7. GET `/analytics/teacher/assessments/{assessment_id}/monitoring`

Monitor assessment completion and response consistency.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| assessment_id | UUID | The assessment ID |

#### Response

```json
{
  "success": true,
  "data": {
    "assessment_id": "uuid",
    "template_name": "Wellbeing Check",
    "title": "Weekly Wellbeing Assessment",
    "class_name": "Grade 5A",
    "total_questions": 10,
    "question_ids": ["q1", "q2", "q3"],
    "summary": {
      "expected_students": 30,
      "completed": 25,
      "incomplete": 3,
      "not_started": 2,
      "unexpected_responses": 0,
      "completion_rate": 83.3
    },
    "completed_students": [
      {
        "student_id": "uuid",
        "student_name": "Alice Johnson",
        "expected_questions": 10,
        "answered_questions": 10,
        "missing_questions": [],
        "extra_questions": [],
        "completed_at": "2025-12-10T14:30:00Z",
        "total_score": 35
      }
    ],
    "incomplete_students": [
      {
        "student_id": "uuid",
        "student_name": "Bob Wilson",
        "expected_questions": 10,
        "answered_questions": 7,
        "missing_questions": ["q8", "q9", "q10"],
        "extra_questions": [],
        "completed_at": null,
        "total_score": 24
      }
    ],
    "not_started_students": [
      {
        "student_id": "uuid",
        "student_name": "Charlie Brown"
      }
    ],
    "unexpected_students": []
  }
}
```

---

### 8. GET `/analytics/teacher/assessments/{assessment_id}/question-breakdown`

Get detailed question-by-question breakdown for an assessment.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| assessment_id | UUID | The assessment ID |

#### Response

```json
{
  "success": true,
  "data": {
    "assessment_id": "uuid",
    "template_name": "Wellbeing Check",
    "title": "Weekly Wellbeing Assessment",
    "total_questions": 10,
    "question_breakdown": [
      {
        "question_id": "q1",
        "question_text": "How are you feeling today?",
        "question_type": "scale",
        "response_count": 25,
        "average_score": 3.5,
        "min_score": 1,
        "max_score": 5,
        "responses": [
          {
            "student_id": "uuid",
            "student_name": "Alice Johnson",
            "answer": 4,
            "score": 4
          }
        ]
      }
    ]
  }
}
```

---

## Additional TypeScript Interfaces

```typescript
// Student Assessment
interface StudentAssessment {
  assessment_id: string;
  template_id: string;
  template_name: string;
  category: string;
  completed_at: string | null;
  total_score: number;
  max_score: number;
  total_questions: number;
  questions_answered: number;
  risk_level: "low" | "medium" | "high";
  responses?: AssessmentResponse[];
}

interface AssessmentResponse {
  question_id: string;
  question_text: string;
  answer_value: number | string;
  score: number | null;
}

interface StudentAssessmentsResponse {
  student_id: string;
  student_name: string;
  total_assessments: number;
  assessments: StudentAssessment[];
}

// Assessment Monitoring
interface CompletedStudent {
  student_id: string;
  student_name: string;
  expected_questions: number;
  answered_questions: number;
  missing_questions: string[];
  extra_questions: string[];
  completed_at: string | null;
  total_score: number;
}

interface NotStartedStudent {
  student_id: string;
  student_name: string;
}

interface AssessmentMonitoringSummary {
  expected_students: number;
  completed: number;
  incomplete: number;
  not_started: number;
  unexpected_responses: number;
  completion_rate: number;
}

interface AssessmentMonitoringResponse {
  assessment_id: string;
  template_name: string;
  title: string;
  class_name: string | null;
  total_questions: number;
  question_ids: string[];
  summary: AssessmentMonitoringSummary;
  completed_students: CompletedStudent[];
  incomplete_students: CompletedStudent[];
  not_started_students: NotStartedStudent[];
  unexpected_students: any[];
}

// Question Breakdown
interface QuestionResponse {
  student_id: string;
  student_name: string;
  answer: number | string;
  score: number | null;
}

interface QuestionBreakdown {
  question_id: string;
  question_text: string;
  question_type: string | null;
  response_count: number;
  average_score: number | null;
  min_score: number | null;
  max_score: number | null;
  responses: QuestionResponse[];
}

interface QuestionBreakdownResponse {
  assessment_id: string;
  template_name: string;
  title: string;
  total_questions: number;
  question_breakdown: QuestionBreakdown[];
}
```

---

## Updated API Service

```typescript
// Add to teacherAnalyticsApi object:

async getStudentAssessments(
  studentId: string,
  params?: { include_responses?: boolean; days?: number }
): Promise<StudentAssessmentsResponse> {
  const query = new URLSearchParams();
  if (params?.include_responses) query.append("include_responses", "true");
  if (params?.days) query.append("days", params.days.toString());
  
  const queryStr = query.toString() ? `?${query}` : "";
  const response = await fetch(`${API_BASE}/students/${studentId}/assessments${queryStr}`);
  if (!response.ok) throw new Error("Failed to fetch student assessments");
  const json = await response.json();
  return json.data;
},

async getAssessmentMonitoring(assessmentId: string): Promise<AssessmentMonitoringResponse> {
  const response = await fetch(`${API_BASE}/assessments/${assessmentId}/monitoring`);
  if (!response.ok) throw new Error("Assessment not found");
  const json = await response.json();
  return json.data;
},

async getAssessmentQuestionBreakdown(assessmentId: string): Promise<QuestionBreakdownResponse> {
  const response = await fetch(`${API_BASE}/assessments/${assessmentId}/question-breakdown`);
  if (!response.ok) throw new Error("Assessment not found");
  const json = await response.json();
  return json.data;
}
```


---

## React Query Hooks for Assessments

```typescript
export function useStudentAssessments(
  studentId: string,
  includeResponses = false,
  days?: number
) {
  return useQuery({
    queryKey: ["student-assessments", studentId, includeResponses, days],
    queryFn: () => teacherAnalyticsApi.getStudentAssessments(studentId, { 
      include_responses: includeResponses, 
      days 
    }),
    enabled: !!studentId,
  });
}

export function useAssessmentMonitoring(assessmentId: string) {
  return useQuery({
    queryKey: ["assessment-monitoring", assessmentId],
    queryFn: () => teacherAnalyticsApi.getAssessmentMonitoring(assessmentId),
    enabled: !!assessmentId,
  });
}

export function useAssessmentQuestionBreakdown(assessmentId: string) {
  return useQuery({
    queryKey: ["assessment-question-breakdown", assessmentId],
    queryFn: () => teacherAnalyticsApi.getAssessmentQuestionBreakdown(assessmentId),
    enabled: !!assessmentId,
  });
}
```

---

## Notes

1. **Data Scope**: All endpoints only return data for classes where the teacher is assigned via `classes.teacher_id`
2. **Risk Levels**: "high" includes both HIGH and CRITICAL risk levels
3. **Pagination**: The `/students` endpoint supports pagination with max 100 items per page
4. **Date Format**: `last_active` is returned in ISO 8601 format with timezone
5. **Student Details**: For detailed student info, use the shared counsellor endpoint: `GET /analytics/counsellor/students/{student_id}`
6. **Assessment Monitoring**: Use to track completion rates and identify students who haven't started or have incomplete responses
