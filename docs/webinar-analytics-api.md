# Webinar Analytics API Documentation

## Base URL
```
/api/v1/analytics/webinars
```

## TypeScript Types

```typescript
// Enums
type WebinarStatus = 'Upcoming' | 'Live' | 'Recorded' | 'Cancelled';
type WebinarCategory = 'Student Wellbeing' | 'Mental Health' | 'Crisis Management' | 
  'Professional Development' | 'Communication' | 'Self-Care' | 'Safety' | 
  'Learning Disabilities' | 'Counseling Skills' | 'Curriculum' | 'Inclusion';
type WebinarAudience = 'Students' | 'Teachers' | 'Parents' | 'Counsellors' | 'All';

// Analytics Types
interface WebinarAnalytics {
  total_invited: number;
  total_attended: number;
  attendance_rate: number;
  avg_watch_time: number;
}

interface WebinarListItem {
  webinar_id: string;
  title: string;
  description: string | null;
  school_id: string | null;
  class_ids: string[] | null;
  target_audience: WebinarAudience | null;
  target_grades: string[] | null;
  speaker_name: string;
  date: string;
  duration_minutes: number;
  category: WebinarCategory | null;
  status: WebinarStatus | null;
  thumbnail_url: string | null;
  analytics: WebinarAnalytics;
}


interface WebinarDetail {
  webinar_id: string;
  title: string;
  description: string | null;
  school_id: string | null;
  class_ids: string[] | null;
  target_audience: WebinarAudience | null;
  target_grades: string[] | null;
  speaker: {
    name: string;
    title: string | null;
    bio: string | null;
    image_url: string | null;
  };
  schedule: {
    date: string;
    duration_minutes: number;
    status: WebinarStatus | null;
  };
  category: WebinarCategory | null;
  analytics: {
    total_invited: number;
    total_attended: number;
    total_absent: number;
    attendance_rate: number;
    avg_watch_time: number;
    min_watch_time: number;
    max_watch_time: number;
    completion_rate: number;
  };
  class_breakdown: ClassBreakdown[];
  watch_time_distribution: Record<string, number>;
}

interface ClassBreakdown {
  class_id: string;
  class_name: string;
  grade: string;
  invited: number;
  attended: number;
  attendance_rate: number;
}

interface Participant {
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
  status: 'Completed' | 'Partial' | 'Absent';
}
```


## Endpoints

### 1. Get Webinars with Analytics
```
GET /api/v1/analytics/webinars
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| school_id | UUID | - | Filter by school |
| status | string | - | Filter by status |
| days | number | 90 | Filter to last N days |
| skip | number | 0 | Pagination offset |
| limit | number | 20 | Page size |

**Response:**
```json
{
  "success": true,
  "data": {
    "total": 15,
    "skip": 0,
    "limit": 20,
    "webinars": [
      {
        "webinar_id": "uuid",
        "title": "Mental Health Awareness",
        "school_id": "uuid",
        "class_ids": ["uuid1", "uuid2"],
        "target_audience": "Students",
        "speaker_name": "Dr. Smith",
        "date": "2025-12-15T10:00:00",
        "duration_minutes": 60,
        "status": "Upcoming",
        "analytics": {
          "total_invited": 150,
          "total_attended": 120,
          "attendance_rate": 80.0,
          "avg_watch_time": 52.5
        }
      }
    ]
  }
}
```


### 2. Get Single Webinar Analytics
```
GET /api/v1/analytics/webinars/{webinar_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "webinar_id": "uuid",
    "title": "Mental Health Awareness",
    "school_id": "uuid",
    "class_ids": ["uuid1", "uuid2"],
    "target_audience": "Students",
    "speaker": {
      "name": "Dr. Smith",
      "title": "Clinical Psychologist",
      "bio": "Expert in adolescent mental health",
      "image_url": "https://..."
    },
    "schedule": {
      "date": "2025-12-15T10:00:00",
      "duration_minutes": 60,
      "status": "Recorded"
    },
    "analytics": {
      "total_invited": 150,
      "total_attended": 120,
      "total_absent": 30,
      "attendance_rate": 80.0,
      "avg_watch_time": 52.5,
      "min_watch_time": 15,
      "max_watch_time": 60,
      "completion_rate": 87.5
    },
    "class_breakdown": [
      {
        "class_id": "uuid",
        "class_name": "8A",
        "grade": "8",
        "invited": 30,
        "attended": 25,
        "attendance_rate": 83.3
      }
    ],
    "watch_time_distribution": {
      "0-25%": 5,
      "25-50%": 10,
      "50-75%": 25,
      "75-100%": 80
    }
  }
}
```


### 3. Get Webinar Participants
```
GET /api/v1/analytics/webinars/{webinar_id}/participants
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| attended | boolean | Filter by attendance |
| class_id | UUID | Filter by class |
| search | string | Search by student name |
| skip | number | Pagination offset |
| limit | number | Page size (default: 50) |

**Response:**
```json
{
  "success": true,
  "data": {
    "webinar_id": "uuid",
    "title": "Mental Health Awareness",
    "total_participants": 150,
    "skip": 0,
    "limit": 50,
    "participants": [
      {
        "student_id": "uuid",
        "student_name": "John Doe",
        "class_id": "uuid",
        "class_name": "8A",
        "grade": "8",
        "attended": true,
        "join_time": "2025-12-15T09:58:00",
        "leave_time": "2025-12-15T10:55:00",
        "watch_duration_minutes": 57,
        "watch_percentage": 95.0,
        "status": "Completed"
      }
    ]
  }
}
```


### 4. Assign Webinar to Classes
```
POST /api/v1/analytics/webinars/{webinar_id}/assign
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| school_id | UUID | Yes | Target school |
| class_ids | UUID[] | No | Specific classes |
| grades | string[] | No | Target grades |

**Response:**
```json
{
  "success": true,
  "data": {
    "webinar_id": "uuid",
    "school_id": "uuid",
    "class_ids": ["uuid1", "uuid2"],
    "target_grades": ["8", "9"],
    "total_students_assigned": 150,
    "new_records_created": 120,
    "existing_records": 30
  }
}
```

### 5. School Webinar Summary
```
GET /api/v1/analytics/webinars/school/{school_id}/summary
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| days | number | 30 | Filter to last N days |

**Response:**
```json
{
  "success": true,
  "data": {
    "school_id": "uuid",
    "period_days": 30,
    "total_webinars": 8,
    "summary": {
      "total_student_invites": 1200,
      "total_attended": 960,
      "overall_attendance_rate": 80.0,
      "avg_watch_time": 48.5
    },
    "by_status": {
      "Upcoming": 2,
      "Recorded": 5,
      "Live": 1
    },
    "by_category": {
      "Mental Health": 3,
      "Student Wellbeing": 2,
      "Safety": 3
    },
    "upcoming": 2,
    "completed": 5
  }
}
```


## API Client Example

```typescript
// webinarAnalyticsApi.ts
import axios from 'axios';

const API_BASE = '/api/v1/analytics/webinars';

export const webinarAnalyticsApi = {
  // Get webinars with analytics
  getWebinars: async (params?: {
    school_id?: string;
    status?: string;
    days?: number;
    skip?: number;
    limit?: number;
  }) => {
    const { data } = await axios.get(API_BASE, { params });
    return data.data;
  },

  // Get single webinar analytics
  getWebinar: async (webinarId: string) => {
    const { data } = await axios.get(`${API_BASE}/${webinarId}`);
    return data.data;
  },

  // Get participants
  getParticipants: async (webinarId: string, params?: {
    attended?: boolean;
    class_id?: string;
    search?: string;
    skip?: number;
    limit?: number;
  }) => {
    const { data } = await axios.get(`${API_BASE}/${webinarId}/participants`, { params });
    return data.data;
  },

  // Assign webinar to classes
  assignWebinar: async (webinarId: string, params: {
    school_id: string;
    class_ids?: string[];
    grades?: string[];
  }) => {
    const { data } = await axios.post(`${API_BASE}/${webinarId}/assign`, null, { params });
    return data.data;
  },

  // Get school summary
  getSchoolSummary: async (schoolId: string, days?: number) => {
    const { data } = await axios.get(`${API_BASE}/school/${schoolId}/summary`, {
      params: { days }
    });
    return data.data;
  }
};
```


## React Component Examples

### Webinar List with Analytics
```tsx
import { useState, useEffect } from 'react';
import { webinarAnalyticsApi, WebinarListItem } from './webinarAnalyticsApi';

export function WebinarList({ schoolId }: { schoolId: string }) {
  const [webinars, setWebinars] = useState<WebinarListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    webinarAnalyticsApi.getWebinars({ school_id: schoolId })
      .then(data => setWebinars(data.webinars))
      .finally(() => setLoading(false));
  }, [schoolId]);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="grid gap-4">
      {webinars.map(webinar => (
        <div key={webinar.webinar_id} className="p-4 border rounded-lg">
          <h3 className="font-semibold">{webinar.title}</h3>
          <p className="text-sm text-gray-500">{webinar.speaker_name}</p>
          <div className="mt-2 flex gap-4 text-sm">
            <span>Invited: {webinar.analytics.total_invited}</span>
            <span>Attended: {webinar.analytics.total_attended}</span>
            <span className="font-medium">
              {webinar.analytics.attendance_rate}% attendance
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
```


### Webinar Detail with Participants
```tsx
import { useState, useEffect } from 'react';
import { webinarAnalyticsApi, WebinarDetail, Participant } from './webinarAnalyticsApi';

export function WebinarDetail({ webinarId }: { webinarId: string }) {
  const [webinar, setWebinar] = useState<WebinarDetail | null>(null);
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [filter, setFilter] = useState<boolean | undefined>();

  useEffect(() => {
    webinarAnalyticsApi.getWebinar(webinarId).then(setWebinar);
    webinarAnalyticsApi.getParticipants(webinarId, { attended: filter })
      .then(data => setParticipants(data.participants));
  }, [webinarId, filter]);

  if (!webinar) return <div>Loading...</div>;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold">{webinar.title}</h2>
        <p className="text-gray-600">{webinar.speaker.name}</p>
      </div>

      {/* Analytics Cards */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard label="Invited" value={webinar.analytics.total_invited} />
        <StatCard label="Attended" value={webinar.analytics.total_attended} />
        <StatCard label="Attendance Rate" value={`${webinar.analytics.attendance_rate}%`} />
        <StatCard label="Avg Watch Time" value={`${webinar.analytics.avg_watch_time} min`} />
      </div>

      {/* Watch Time Distribution */}
      <div className="p-4 border rounded">
        <h3 className="font-semibold mb-2">Watch Time Distribution</h3>
        <div className="flex gap-2">
          {Object.entries(webinar.watch_time_distribution).map(([range, count]) => (
            <div key={range} className="flex-1 text-center">
              <div className="text-lg font-bold">{count}</div>
              <div className="text-xs text-gray-500">{range}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Participants Table */}
      <div>
        <div className="flex justify-between mb-2">
          <h3 className="font-semibold">Participants</h3>
          <select onChange={e => setFilter(e.target.value === '' ? undefined : e.target.value === 'true')}>
            <option value="">All</option>
            <option value="true">Attended</option>
            <option value="false">Absent</option>
          </select>
        </div>
        <table className="w-full">
          <thead>
            <tr className="text-left border-b">
              <th>Student</th>
              <th>Class</th>
              <th>Status</th>
              <th>Watch Time</th>
            </tr>
          </thead>
          <tbody>
            {participants.map(p => (
              <tr key={p.student_id} className="border-b">
                <td>{p.student_name}</td>
                <td>{p.class_name}</td>
                <td>
                  <span className={`px-2 py-1 rounded text-xs ${
                    p.status === 'Completed' ? 'bg-green-100 text-green-800' :
                    p.status === 'Partial' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {p.status}
                  </span>
                </td>
                <td>{p.watch_duration_minutes || 0} min ({p.watch_percentage}%)</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="p-4 border rounded text-center">
      <div className="text-2xl font-bold">{value}</div>
      <div className="text-sm text-gray-500">{label}</div>
    </div>
  );
}
```


### School Webinar Dashboard
```tsx
import { useState, useEffect } from 'react';
import { webinarAnalyticsApi } from './webinarAnalyticsApi';

interface SchoolSummary {
  total_webinars: number;
  summary: {
    total_student_invites: number;
    total_attended: number;
    overall_attendance_rate: number;
    avg_watch_time: number;
  };
  by_status: Record<string, number>;
  by_category: Record<string, number>;
  upcoming: number;
  completed: number;
}

export function SchoolWebinarDashboard({ schoolId }: { schoolId: string }) {
  const [summary, setSummary] = useState<SchoolSummary | null>(null);
  const [days, setDays] = useState(30);

  useEffect(() => {
    webinarAnalyticsApi.getSchoolSummary(schoolId, days).then(setSummary);
  }, [schoolId, days]);

  if (!summary) return <div>Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">Webinar Analytics</h2>
        <select value={days} onChange={e => setDays(Number(e.target.value))}>
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <StatCard label="Total Webinars" value={summary.total_webinars} />
        <StatCard label="Students Invited" value={summary.summary.total_student_invites} />
        <StatCard label="Attendance Rate" value={`${summary.summary.overall_attendance_rate}%`} />
        <StatCard label="Avg Watch Time" value={`${summary.summary.avg_watch_time} min`} />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 border rounded">
          <h3 className="font-semibold mb-2">By Status</h3>
          {Object.entries(summary.by_status).map(([status, count]) => (
            <div key={status} className="flex justify-between py-1">
              <span>{status}</span>
              <span className="font-medium">{count}</span>
            </div>
          ))}
        </div>
        <div className="p-4 border rounded">
          <h3 className="font-semibold mb-2">By Category</h3>
          {Object.entries(summary.by_category).map(([cat, count]) => (
            <div key={cat} className="flex justify-between py-1">
              <span>{cat}</span>
              <span className="font-medium">{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```


### Assign Webinar Modal
```tsx
import { useState } from 'react';
import { webinarAnalyticsApi } from './webinarAnalyticsApi';

interface AssignWebinarProps {
  webinarId: string;
  schoolId: string;
  classes: { class_id: string; name: string; grade: string }[];
  onSuccess: () => void;
}

export function AssignWebinarModal({ webinarId, schoolId, classes, onSuccess }: AssignWebinarProps) {
  const [selectedClasses, setSelectedClasses] = useState<string[]>([]);
  const [selectedGrades, setSelectedGrades] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const grades = [...new Set(classes.map(c => c.grade))].sort();

  const handleAssign = async () => {
    setLoading(true);
    try {
      await webinarAnalyticsApi.assignWebinar(webinarId, {
        school_id: schoolId,
        class_ids: selectedClasses.length > 0 ? selectedClasses : undefined,
        grades: selectedGrades.length > 0 ? selectedGrades : undefined
      });
      onSuccess();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 space-y-4">
      <h3 className="font-semibold">Assign Webinar to Students</h3>
      
      <div>
        <label className="block text-sm font-medium mb-1">Select Classes</label>
        <div className="grid grid-cols-3 gap-2">
          {classes.map(cls => (
            <label key={cls.class_id} className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={selectedClasses.includes(cls.class_id)}
                onChange={e => {
                  if (e.target.checked) {
                    setSelectedClasses([...selectedClasses, cls.class_id]);
                  } else {
                    setSelectedClasses(selectedClasses.filter(id => id !== cls.class_id));
                  }
                }}
              />
              {cls.name} ({cls.grade})
            </label>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Or Select Grades</label>
        <div className="flex gap-2">
          {grades.map(grade => (
            <label key={grade} className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={selectedGrades.includes(grade)}
                onChange={e => {
                  if (e.target.checked) {
                    setSelectedGrades([...selectedGrades, grade]);
                  } else {
                    setSelectedGrades(selectedGrades.filter(g => g !== grade));
                  }
                }}
              />
              Grade {grade}
            </label>
          ))}
        </div>
      </div>

      <button
        onClick={handleAssign}
        disabled={loading}
        className="w-full py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? 'Assigning...' : 'Assign Webinar'}
      </button>
    </div>
  );
}
```

## Integration with Student Detail View

The webinar analytics integrates with the existing counsellor analytics student detail view. Use the `/analytics/counsellor/students/{student_id}/webinars` endpoint to get a student's webinar history, which returns attendance records with watch duration and completion status.