# Webinar Registration & Analytics API Documentation

## Base URL
```
/api/v1/analytics/webinars
```

---

## Overview

This API allows schools to:
1. Browse available webinars
2. Register webinars for their school (whole school or specific classes/grades)
3. Track attendance and engagement analytics
4. Monitor completion rates by class

---

## Endpoints

### 1. GET `/analytics/webinars`

Get all webinars with attendance analytics.

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| school_id | UUID | No | - | Filter webinars for a specific school |
| status | string | No | - | Filter by status: "Upcoming", "Live", "Recorded", "Cancelled" |
| days | int | No | 90 | Filter to last N days |
| skip | int | No | 0 | Pagination offset |
| limit | int | No | 20 | Items per page |

#### Response

```json
{
  "success": true,
  "data": {
    "total": 25,
    "skip": 0,
    "limit": 20,
    "webinars": [
      {
        "webinar_id": "uuid",
        "title": "Student Mental Health Awareness",
        "description": "Understanding and supporting student mental health",
        "school_id": "uuid",
        "class_ids": ["uuid1", "uuid2"],
        "target_audience": "Students",
        "target_grades": ["8", "9", "10"],
        "speaker_name": "Dr. Jane Smith",
        "date": "2025-12-15T10:00:00Z",
        "duration_minutes": 60,
        "category": "Mental Health",
        "status": "Upcoming",
        "thumbnail_url": "https://...",
        "analytics": {
          "total_invited": 150,
          "total_attended": 120,
          "attendance_rate": 80.0,
          "avg_watch_time": 45.5
        }
      }
    ]
  }
}
```

---

### 2. GET `/analytics/webinars/{webinar_id}`

Get detailed analytics for a single webinar.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| webinar_id | UUID | The webinar ID |

#### Response

```json
{
  "success": true,
  "data": {
    "webinar_id": "uuid",
    "title": "Student Mental Health Awareness",
    "description": "...",
    "school_id": "uuid",
    "class_ids": ["uuid1", "uuid2"],
    "target_audience": "Students",
    "target_grades": ["8", "9"],
    "speaker": {
      "name": "Dr. Jane Smith",
      "title": "Clinical Psychologist",
      "bio": "...",
      "image_url": "https://..."
    },
    "schedule": {
      "date": "2025-12-15T10:00:00Z",
      "duration_minutes": 60,
      "status": "Recorded"
    },
    "category": "Mental Health",
    "analytics": {
      "total_invited": 150,
      "total_attended": 120,
      "total_absent": 30,
      "attendance_rate": 80.0,
      "avg_watch_time": 45.5,
      "min_watch_time": 5,
      "max_watch_time": 60,
      "completion_rate": 75.8
    },
    "class_breakdown": [
      {
        "class_id": "uuid",
        "class_name": "Grade 8A",
        "grade": "8",
        "invited": 30,
        "attended": 25,
        "attendance_rate": 83.3
      }
    ],
    "watch_time_distribution": {
      "0-25%": 10,
      "25-50%": 15,
      "50-75%": 25,
      "75-100%": 70
    }
  }
}
```

---

### 3. GET `/analytics/webinars/{webinar_id}/participants`

Get participant list for a webinar with attendance details.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| webinar_id | UUID | The webinar ID |

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| attended | bool | No | - | Filter by attendance status |
| class_id | UUID | No | - | Filter by class |
| search | string | No | - | Search by student name |
| skip | int | No | 0 | Pagination offset |
| limit | int | No | 50 | Items per page |

#### Response

```json
{
  "success": true,
  "data": {
    "webinar_id": "uuid",
    "title": "Student Mental Health Awareness",
    "total_participants": 150,
    "skip": 0,
    "limit": 50,
    "participants": [
      {
        "student_id": "uuid",
        "student_name": "Alice Johnson",
        "class_id": "uuid",
        "class_name": "Grade 8A",
        "grade": "8",
        "attended": true,
        "join_time": "2025-12-15T10:02:00Z",
        "leave_time": "2025-12-15T11:00:00Z",
        "watch_duration_minutes": 58,
        "watch_percentage": 96.7,
        "status": "Completed"
      }
    ]
  }
}
```

---

### 4. POST `/analytics/webinars/{webinar_id}/register`

Register a webinar for the school with optional class/grade targeting.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| webinar_id | UUID | The webinar ID |

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| school_id | UUID | Yes | The school ID |
| user_id | UUID | Yes | The user registering the webinar |

#### Request Body

```json
{
  "registration_type": "class",
  "class_ids": ["uuid1", "uuid2"],
  "grade_ids": ["8", "9"],
  "notify_students": true
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| registration_type | string | No | "school" | "school" (all students) or "class" (specific classes/grades) |
| class_ids | UUID[] | No | - | Specific class IDs to target |
| grade_ids | string[] | No | - | Specific grades to target |
| notify_students | bool | No | true | Whether to notify students |

#### Response

```json
{
  "success": true,
  "data": {
    "registration_id": "uuid",
    "webinar_id": "uuid",
    "school_id": "uuid",
    "registration_type": "class",
    "class_ids": ["uuid1", "uuid2"],
    "grade_ids": ["8", "9"],
    "total_students_invited": 60,
    "registered_by": "uuid",
    "registered_at": "2025-12-12T10:00:00Z",
    "status": "Active"
  }
}
```

#### Error Responses

| Code | Detail | Description |
|------|--------|-------------|
| 404 | WEBINAR_NOT_FOUND | Webinar doesn't exist |
| 400 | WEBINAR_CANCELLED | Webinar has been cancelled |
| 400 | ALREADY_REGISTERED | School already registered for this webinar |
| 400 | INVALID_CLASS_IDS | One or more class IDs don't belong to the school |
| 400 | NO_STUDENTS_FOUND | No students found matching the criteria |

---

### 5. GET `/analytics/webinars/registrations`

Get all webinars registered by the school.

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| school_id | UUID | Yes | - | The school ID |
| status | string | No | - | Filter by status: "Active", "Completed", "Cancelled" |
| include_analytics | bool | No | false | Include attendance analytics |

#### Response

```json
{
  "success": true,
  "data": {
    "total_registrations": 10,
    "registrations": [
      {
        "registration_id": "uuid",
        "webinar_id": "uuid",
        "webinar": {
          "title": "Student Mental Health Awareness",
          "speaker_name": "Dr. Jane Smith",
          "date": "2025-12-15T10:00:00Z",
          "duration_minutes": 60,
          "status": "Recorded",
          "category": "Mental Health",
          "thumbnail_url": "https://..."
        },
        "registration_type": "class",
        "class_ids": ["uuid1", "uuid2"],
        "class_names": ["Grade 8A", "Grade 8B"],
        "total_students_invited": 60,
        "registered_at": "2025-12-12T10:00:00Z",
        "analytics": {
          "total_attended": 50,
          "attendance_rate": 83.3,
          "avg_watch_time": 48.5
        }
      }
    ]
  }
}
```

---

### 6. GET `/analytics/webinars/registered`

Get analytics only for webinars that the school has registered for.

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| school_id | UUID | Yes | - | The school ID |
| status | string | No | - | Filter by registration status |
| days | int | No | 30 | Filter to last N days |

#### Response

```json
{
  "success": true,
  "data": {
    "school_id": "uuid",
    "total_registered_webinars": 10,
    "summary": {
      "total_students_invited": 500,
      "total_attended": 420,
      "overall_attendance_rate": 84.0,
      "avg_watch_time": 45.2
    },
    "webinars": [
      {
        "webinar_id": "uuid",
        "title": "Student Mental Health Awareness",
        "speaker_name": "Dr. Jane Smith",
        "date": "2025-12-15T10:00:00Z",
        "status": "Recorded",
        "registration_type": "class",
        "classes_registered": ["Grade 8A", "Grade 8B"],
        "analytics": {
          "total_invited": 60,
          "total_attended": 50,
          "attendance_rate": 83.3,
          "avg_watch_time": 48.5
        }
      }
    ]
  }
}
```

---

### 7. GET `/analytics/webinars/{webinar_id}/class-breakdown`

Get detailed attendance breakdown by class for a registered webinar.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| webinar_id | UUID | The webinar ID |

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| school_id | UUID | Yes | The school ID |

#### Response

```json
{
  "success": true,
  "data": {
    "webinar_id": "uuid",
    "title": "Student Mental Health Awareness",
    "total_classes": 2,
    "class_breakdown": [
      {
        "class_id": "uuid",
        "class_name": "Grade 8A",
        "grade": "8",
        "section": "A",
        "teacher_name": "Mr. John Smith",
        "total_students": 30,
        "invited": 30,
        "attended": 25,
        "attendance_rate": 83.3,
        "avg_watch_time": 48.5,
        "completion_rate": 76.7,
        "students": [
          {
            "student_id": "uuid",
            "student_name": "Alice Johnson",
            "attended": true,
            "watch_duration_minutes": 58,
            "watch_percentage": 96.7,
            "status": "Completed"
          }
        ]
      }
    ]
  }
}
```

---

### 8. POST `/analytics/webinars/{webinar_id}/unregister`

Unregister a webinar and remove all student invitations.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| webinar_id | UUID | The webinar ID |

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| school_id | UUID | Yes | The school ID |

#### Response

```json
{
  "success": true,
  "data": {
    "webinar_id": "uuid",
    "school_id": "uuid",
    "students_removed": 60,
    "unregistered_at": "2025-12-12T15:00:00Z"
  }
}
```

---

## TypeScript Interfaces

```typescript
// Webinar Analytics
interface WebinarAnalytics {
  total_invited: number;
  total_attended: number;
  attendance_rate: number;
  avg_watch_time: number;
}

interface WebinarItem {
  webinar_id: string;
  title: string;
  description: string | null;
  school_id: string | null;
  class_ids: string[] | null;
  target_audience: string | null;
  target_grades: string[] | null;
  speaker_name: string;
  date: string;
  duration_minutes: number;
  category: string | null;
  status: string | null;
  thumbnail_url: string | null;
  analytics: WebinarAnalytics;
}

interface WebinarListResponse {
  total: number;
  skip: number;
  limit: number;
  webinars: WebinarItem[];
}

// Registration
interface RegistrationRequest {
  registration_type: "school" | "class";
  class_ids?: string[];
  grade_ids?: string[];
  notify_students?: boolean;
}

interface RegistrationResponse {
  registration_id: string;
  webinar_id: string;
  school_id: string;
  registration_type: "school" | "class";
  class_ids: string[];
  grade_ids: string[];
  total_students_invited: number;
  registered_by: string;
  registered_at: string;
  status: "Active" | "Completed" | "Cancelled";
}

// My Registrations
interface WebinarInfo {
  title: string | null;
  speaker_name: string | null;
  date: string | null;
  duration_minutes: number | null;
  status: string | null;
  category: string | null;
  thumbnail_url: string | null;
}

interface RegistrationItem {
  registration_id: string;
  webinar_id: string;
  webinar: WebinarInfo;
  registration_type: "school" | "class";
  class_ids: string[];
  class_names: string[];
  total_students_invited: number;
  registered_at: string;
  analytics: WebinarAnalytics | null;
}

interface MyRegistrationsResponse {
  total_registrations: number;
  registrations: RegistrationItem[];
}

// Registered Webinars Analytics
interface RegisteredWebinarSummary {
  total_students_invited: number;
  total_attended: number;
  overall_attendance_rate: number;
  avg_watch_time: number;
}

interface RegisteredWebinarItem {
  webinar_id: string;
  title: string | null;
  speaker_name: string | null;
  date: string | null;
  status: string | null;
  registration_type: "school" | "class";
  classes_registered: string[];
  analytics: WebinarAnalytics;
}

interface RegisteredWebinarsResponse {
  school_id: string;
  total_registered_webinars: number;
  summary: RegisteredWebinarSummary;
  webinars: RegisteredWebinarItem[];
}

// Class Breakdown
interface StudentAttendance {
  student_id: string;
  student_name: string;
  attended: boolean;
  watch_duration_minutes: number | null;
  watch_percentage: number;
  status: "Completed" | "Partial" | "Absent";
}

interface ClassBreakdownItem {
  class_id: string;
  class_name: string;
  grade: string;
  section: string | null;
  teacher_name: string | null;
  total_students: number;
  invited: number;
  attended: number;
  attendance_rate: number;
  avg_watch_time: number;
  completion_rate: number;
  students: StudentAttendance[];
}

interface ClassBreakdownResponse {
  webinar_id: string;
  title: string;
  total_classes: number;
  class_breakdown: ClassBreakdownItem[];
}

// Participants
interface ParticipantItem {
  student_id: string;
  student_name: string;
  class_id: string | null;
  class_name: string | null;
  grade: string | null;
  attended: boolean;
  join_time: string | null;
  leave_time: string | null;
  watch_duration_minutes: number | null;
  watch_percentage: number;
  status: "Completed" | "Partial" | "Absent";
}

interface ParticipantsResponse {
  webinar_id: string;
  title: string;
  total_participants: number;
  skip: number;
  limit: number;
  participants: ParticipantItem[];
}
```

---

## API Service

```typescript
const API_BASE = "/api/v1/analytics/webinars";

export const webinarApi = {
  // Get all webinars with analytics
  async getWebinars(params?: {
    school_id?: string;
    status?: string;
    days?: number;
    skip?: number;
    limit?: number;
  }): Promise<WebinarListResponse> {
    const query = new URLSearchParams();
    if (params?.school_id) query.append("school_id", params.school_id);
    if (params?.status) query.append("status", params.status);
    if (params?.days) query.append("days", params.days.toString());
    if (params?.skip) query.append("skip", params.skip.toString());
    if (params?.limit) query.append("limit", params.limit.toString());
    
    const response = await fetch(`${API_BASE}?${query}`);
    const json = await response.json();
    return json.data;
  },

  // Get single webinar details
  async getWebinar(webinarId: string): Promise<any> {
    const response = await fetch(`${API_BASE}/${webinarId}`);
    if (!response.ok) throw new Error("Webinar not found");
    const json = await response.json();
    return json.data;
  },

  // Get webinar participants
  async getParticipants(
    webinarId: string,
    params?: { attended?: boolean; class_id?: string; search?: string; skip?: number; limit?: number }
  ): Promise<ParticipantsResponse> {
    const query = new URLSearchParams();
    if (params?.attended !== undefined) query.append("attended", params.attended.toString());
    if (params?.class_id) query.append("class_id", params.class_id);
    if (params?.search) query.append("search", params.search);
    if (params?.skip) query.append("skip", params.skip.toString());
    if (params?.limit) query.append("limit", params.limit.toString());
    
    const response = await fetch(`${API_BASE}/${webinarId}/participants?${query}`);
    const json = await response.json();
    return json.data;
  },

  // Register webinar for school
  async registerWebinar(
    webinarId: string,
    schoolId: string,
    userId: string,
    request: RegistrationRequest
  ): Promise<RegistrationResponse> {
    const response = await fetch(
      `${API_BASE}/${webinarId}/register?school_id=${schoolId}&user_id=${userId}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request)
      }
    );
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Registration failed");
    }
    const json = await response.json();
    return json.data;
  },

  // Get my registrations
  async getMyRegistrations(
    schoolId: string,
    params?: { status?: string; include_analytics?: boolean }
  ): Promise<MyRegistrationsResponse> {
    const query = new URLSearchParams();
    query.append("school_id", schoolId);
    if (params?.status) query.append("status", params.status);
    if (params?.include_analytics) query.append("include_analytics", "true");
    
    const response = await fetch(`${API_BASE}/registrations?${query}`);
    const json = await response.json();
    return json.data;
  },

  // Get registered webinars analytics
  async getRegisteredAnalytics(
    schoolId: string,
    params?: { status?: string; days?: number }
  ): Promise<RegisteredWebinarsResponse> {
    const query = new URLSearchParams();
    query.append("school_id", schoolId);
    if (params?.status) query.append("status", params.status);
    if (params?.days) query.append("days", params.days.toString());
    
    const response = await fetch(`${API_BASE}/registered?${query}`);
    const json = await response.json();
    return json.data;
  },

  // Get class breakdown
  async getClassBreakdown(webinarId: string, schoolId: string): Promise<ClassBreakdownResponse> {
    const response = await fetch(`${API_BASE}/${webinarId}/class-breakdown?school_id=${schoolId}`);
    if (!response.ok) throw new Error("Not registered for this webinar");
    const json = await response.json();
    return json.data;
  },

  // Unregister webinar
  async unregisterWebinar(webinarId: string, schoolId: string): Promise<any> {
    const response = await fetch(
      `${API_BASE}/${webinarId}/unregister?school_id=${schoolId}`,
      { method: "POST" }
    );
    if (!response.ok) throw new Error("Unregistration failed");
    const json = await response.json();
    return json.data;
  }
};
```

---

## React Query Hooks

```typescript
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { webinarApi } from "./webinarApi";

// Get all webinars
export function useWebinars(params?: {
  school_id?: string;
  status?: string;
  days?: number;
}) {
  return useQuery({
    queryKey: ["webinars", params],
    queryFn: () => webinarApi.getWebinars(params),
  });
}

// Get single webinar
export function useWebinar(webinarId: string) {
  return useQuery({
    queryKey: ["webinar", webinarId],
    queryFn: () => webinarApi.getWebinar(webinarId),
    enabled: !!webinarId,
  });
}

// Get participants
export function useWebinarParticipants(
  webinarId: string,
  params?: { attended?: boolean; class_id?: string }
) {
  return useQuery({
    queryKey: ["webinar-participants", webinarId, params],
    queryFn: () => webinarApi.getParticipants(webinarId, params),
    enabled: !!webinarId,
  });
}

// Get my registrations
export function useMyRegistrations(schoolId: string, includeAnalytics = false) {
  return useQuery({
    queryKey: ["my-registrations", schoolId, includeAnalytics],
    queryFn: () => webinarApi.getMyRegistrations(schoolId, { include_analytics: includeAnalytics }),
    enabled: !!schoolId,
  });
}

// Get registered webinars analytics
export function useRegisteredAnalytics(schoolId: string, days = 30) {
  return useQuery({
    queryKey: ["registered-analytics", schoolId, days],
    queryFn: () => webinarApi.getRegisteredAnalytics(schoolId, { days }),
    enabled: !!schoolId,
  });
}

// Get class breakdown
export function useClassBreakdown(webinarId: string, schoolId: string) {
  return useQuery({
    queryKey: ["class-breakdown", webinarId, schoolId],
    queryFn: () => webinarApi.getClassBreakdown(webinarId, schoolId),
    enabled: !!webinarId && !!schoolId,
  });
}

// Register webinar mutation
export function useRegisterWebinar() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({
      webinarId,
      schoolId,
      userId,
      request
    }: {
      webinarId: string;
      schoolId: string;
      userId: string;
      request: RegistrationRequest;
    }) => webinarApi.registerWebinar(webinarId, schoolId, userId, request),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["my-registrations", variables.schoolId] });
      queryClient.invalidateQueries({ queryKey: ["registered-analytics", variables.schoolId] });
    },
  });
}

// Unregister webinar mutation
export function useUnregisterWebinar() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ webinarId, schoolId }: { webinarId: string; schoolId: string }) =>
      webinarApi.unregisterWebinar(webinarId, schoolId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["my-registrations", variables.schoolId] });
      queryClient.invalidateQueries({ queryKey: ["registered-analytics", variables.schoolId] });
    },
  });
}
```

---

## Usage Examples

### Register a Webinar for Specific Classes

```typescript
const { mutate: register, isLoading } = useRegisterWebinar();

const handleRegister = () => {
  register({
    webinarId: "webinar-uuid",
    schoolId: "school-uuid",
    userId: "user-uuid",
    request: {
      registration_type: "class",
      class_ids: ["class-1-uuid", "class-2-uuid"],
      notify_students: true
    }
  });
};
```

### Display Registered Webinars with Analytics

```tsx
function RegisteredWebinars({ schoolId }: { schoolId: string }) {
  const { data, isLoading } = useRegisteredAnalytics(schoolId);
  
  if (isLoading) return <Spinner />;
  
  return (
    <div>
      <h2>Summary</h2>
      <p>Total Invited: {data.summary.total_students_invited}</p>
      <p>Total Attended: {data.summary.total_attended}</p>
      <p>Attendance Rate: {data.summary.overall_attendance_rate}%</p>
      
      <h2>Webinars</h2>
      {data.webinars.map(w => (
        <WebinarCard key={w.webinar_id} webinar={w} />
      ))}
    </div>
  );
}
```

### View Class Breakdown

```tsx
function ClassBreakdown({ webinarId, schoolId }: Props) {
  const { data, isLoading } = useClassBreakdown(webinarId, schoolId);
  
  if (isLoading) return <Spinner />;
  
  return (
    <div>
      <h2>{data.title}</h2>
      {data.class_breakdown.map(cls => (
        <div key={cls.class_id}>
          <h3>{cls.class_name}</h3>
          <p>Attendance: {cls.attended}/{cls.total_students} ({cls.attendance_rate}%)</p>
          <p>Avg Watch Time: {cls.avg_watch_time} mins</p>
          
          <table>
            <thead>
              <tr>
                <th>Student</th>
                <th>Status</th>
                <th>Watch %</th>
              </tr>
            </thead>
            <tbody>
              {cls.students.map(s => (
                <tr key={s.student_id}>
                  <td>{s.student_name}</td>
                  <td>{s.status}</td>
                  <td>{s.watch_percentage}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
}
```

---

## Notes

1. **Registration Types**:
   - `school`: All students in the school are invited
   - `class`: Only students in specified classes/grades are invited

2. **Watch Status**:
   - `Completed`: Watched 75%+ of the webinar
   - `Partial`: Watched some but less than 75%
   - `Absent`: Did not attend

3. **Unique Registration**: Each school can only register once per webinar. Use unregister to remove and re-register with different settings.

4. **Analytics**: Analytics are calculated based on `StudentWebinarAttendance` records created during registration.
