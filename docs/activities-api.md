# Activities API Documentation

## Overview

The Activities API returns data from both **curated** (`activities` table) and **generated** (`generatedactivities` table) sources. Returns all database columns plus raw `activity_data` JSONB.

---

## Endpoints

### GET `/api/v1/activities/`

Retrieve all activities with optional filtering.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | int | 0 | Pagination offset |
| `limit` | int | 100 | Max records to return |
| `age` | int | null | Filter by exact age |
| `diagnosis` | string | null | Filter by diagnosis (case-insensitive) |
| `themes` | string | null | Filter by themes (comma-separated) |
| `source` | string | "all" | `all`, `curated`, or `generated` |
| `include_flashcards` | bool | false | Include S3 flashcard images |

#### Example Requests

```bash
GET /api/v1/activities/
GET /api/v1/activities/?source=curated
GET /api/v1/activities/?source=generated
GET /api/v1/activities/?age=8&diagnosis=ADHD
```

### GET `/api/v1/activities/{activity_id}`

Retrieve a specific activity by ID. Searches both tables.

---

## Response Examples

### List Response

```json
{
  "filters": {
    "age": null,
    "diagnosis": null,
    "themes": null,
    "source": "all"
  },
  "total_count": 1713,
  "count": 2,
  "activities": [...]
}
```

### Curated Activity Response

```json
{
  "id": 65,
  "activity_id": "cb3a8cf0-ff48-4ce3-8f63-b67c7a50da70",
  "activity_name": "Disability History Timeline",
  "framework": "",
  "age": 16,
  "diagnosis": "Learning Disabilities",
  "cognitive": "",
  "sensory": "",
  "themes": "Creativity & Imagination",
  "setting": "Classroom and school hallways",
  "supervision": "Teacher",
  "duration_pref": "30+ mins",
  "risk_level": "Medium",
  "skill_level": "High",
  "activity_data": {
    "Age": 16,
    "Type": "General",
    "Themes": ["Creativity & Imagination"],
    "Sensory": "",
    "Setting": "Classroom and school hallways",
    "Age Band": "15-18 years",
    "Duration": "10–20 minutes",
    "Elements": [],
    "Cognitive": "",
    "Diagnosis": "Learning Disabilities",
    "Framework": "",
    "Risk Level": "Medium",
    "Activity ID": "cb3a8cf0-ff48-4ce3-8f63-b67c7a50da70",
    "Facilitator": "This activity should be facilitated by the classroom teacher...",
    "Skill Level": "High",
    "Therapy Goal": "Develop a sense of pride and connection...",
    "Activity Name": "Disability History Timeline",
    "Learning Goal": "Practice research, visual design and chronological reasoning skills.",
    "Flashcard Prompts": [
      {
        "Style": "child-friendly, simple, colourful, no text",
        "Context": "Introducing the concept of disability history",
        "Image_name": null,
        "What to draw": "A diverse group of people with various disabilities..."
      }
    ],
    "Full Instructions": [
      "Introduce the concept of disability rights history...",
      "Divide the class into small research groups..."
    ],
    "Supervision Level": "Teacher",
    "Materials Required": [
      "Computers or tablets with internet access for research",
      "History books and articles on disability rights",
      "Large poster boards or roll paper for the timeline sections"
    ],
    "Duration Preference": "30+ mins",
    "Environment Setting": "The research portion will occur in the classroom...",
    "Safety Requirements": [
      "Ensure students are using reliable sources for research...",
      "Provide content warnings if any research materials contain descriptions of abuse..."
    ],
    "Activity Description": "In this activity, students will research key events...",
    "Activity Success Criteria": [
      "Students can identify several key events, laws, and leaders...",
      "Small groups collaborate effectively..."
    ]
  },
  "source": "curated",
  "flashcards": null
}
```

### Generated Activity Response

```json
{
  "id": 952,
  "activity_id": "a2f54eb9-e7b7-45e5-acd6-07e5f58e554a",
  "activity_name": "Storytelling Charades",
  "framework": "",
  "age": 7,
  "diagnosis": "",
  "cognitive": "",
  "sensory": "",
  "themes": "Emotional Regulation, Social Skills & Empathy",
  "setting": "Living room or playroom at home",
  "supervision": "Parent",
  "duration_pref": "10–20 mins",
  "risk_level": "Low",
  "skill_level": "Medium",
  "activity_data": {
    "Age": 7,
    "Type": "General",
    "Themes": ["Emotional Regulation", "Social Skills & Empathy"],
    "Sensory": "",
    "Setting": "Living room or playroom at home",
    "Age Band": "7-9 years",
    "Elements": ["Alphabets", "Fruits"],
    "Cognitive": "",
    "Diagnosis": "",
    "Framework": "",
    "Risk Level": "Low",
    "Activity ID": "a2f54eb9-e7b7-45e5-acd6-07e5f58e554a",
    "Skill Level": "Medium",
    "Therapy Goal": "Improve ability to convey ideas non-verbally...",
    "Activity Name": "Storytelling Charades",
    "Learning Goal": "Develop skills in expressive communication...",
    "Supervision Level": "Parent",
    "Duration Preference": "10–20 mins",
    "Activity Description": "Children take turns acting out scenes from a familiar story..."
  },
  "source": "generated",
  "flashcards": null
}
```

---

## Frontend TypeScript Interfaces

```typescript
interface FlashcardPrompt {
  Style: string;
  Context: string;
  Image_name: string | null;
  "What to draw": string;
}

// Curated activities have all fields
interface CuratedActivityData {
  Age: number;
  Type: string;
  Themes: string[];
  Sensory: string;
  Setting: string;
  "Age Band": string;
  Duration: string;
  Elements: string[];
  Cognitive: string;
  Diagnosis: string;
  Framework: string;
  "Risk Level": string;
  "Activity ID": string;
  Facilitator: string;
  "Skill Level": string;
  "Therapy Goal": string;
  "Activity Name": string;
  "Learning Goal": string;
  "Flashcard Prompts": FlashcardPrompt[];
  "Full Instructions": string[];
  "Supervision Level": string;
  "Materials Required": string[];
  "Duration Preference": string;
  "Environment Setting": string;
  "Safety Requirements": string[];
  "Activity Description": string;
  "Activity Success Criteria": string[];
}

// Generated activities have fewer fields (no instructions, materials, safety, etc.)
interface GeneratedActivityData {
  Age: number;
  Type: string;
  Themes: string[];
  Sensory: string;
  Setting: string;
  "Age Band": string;
  Elements: string[];
  Cognitive: string;
  Diagnosis: string;
  Framework: string;
  "Risk Level": string;
  "Activity ID": string;
  "Skill Level": string;
  "Therapy Goal": string;
  "Activity Name": string;
  "Learning Goal": string;
  "Supervision Level": string;
  "Duration Preference": string;
  "Activity Description": string;
}

// Union type for activity_data
type ActivityData = CuratedActivityData | GeneratedActivityData;

interface Activity {
  // Database columns
  id: number;
  activity_id: string;
  activity_name: string;
  framework: string;
  age: number;
  diagnosis: string;
  cognitive: string;
  sensory: string;
  themes: string;  // comma-separated string
  setting: string;
  supervision: string;
  duration_pref: string;
  risk_level: string;
  skill_level: string;
  
  // Raw JSONB from database
  activity_data: ActivityData;
  
  // Metadata
  source: "curated" | "generated";
  flashcards: string[] | null;
}

interface ActivitiesResponse {
  filters: {
    age: number | null;
    diagnosis: string | null;
    themes: string[] | null;
    source: string;
  };
  total_count: number;
  count: number;
  activities: Activity[];
}
```


---

## API Service Example

```typescript
type ActivitySource = "all" | "curated" | "generated";

interface GetActivitiesParams {
  skip?: number;
  limit?: number;
  age?: number;
  diagnosis?: string;
  themes?: string;
  source?: ActivitySource;
  include_flashcards?: boolean;
}

const API_BASE = "/api/v1";

export async function getActivities(params: GetActivitiesParams = {}): Promise<ActivitiesResponse> {
  const queryParams = new URLSearchParams();
  
  if (params.skip) queryParams.append("skip", params.skip.toString());
  if (params.limit) queryParams.append("limit", params.limit.toString());
  if (params.age) queryParams.append("age", params.age.toString());
  if (params.diagnosis) queryParams.append("diagnosis", params.diagnosis);
  if (params.themes) queryParams.append("themes", params.themes);
  if (params.source) queryParams.append("source", params.source);
  if (params.include_flashcards) queryParams.append("include_flashcards", "true");
  
  const response = await fetch(`${API_BASE}/activities/?${queryParams}`);
  if (!response.ok) throw new Error("Failed to fetch activities");
  return response.json();
}

export async function getActivity(activityId: string, includeFlashcards = false): Promise<Activity> {
  const params = includeFlashcards ? "?include_flashcards=true" : "";
  const response = await fetch(`${API_BASE}/activities/${activityId}${params}`);
  if (!response.ok) throw new Error("Activity not found");
  return response.json();
}
```

---

## Key Differences: Curated vs Generated

| Field | Curated | Generated |
|-------|---------|-----------|
| `Materials Required` | ✅ Array of strings | ❌ Not present |
| `Safety Requirements` | ✅ Array of strings | ❌ Not present |
| `Full Instructions` | ✅ Array of strings | ❌ Not present |
| `Activity Success Criteria` | ✅ Array of strings | ❌ Not present |
| `Flashcard Prompts` | ✅ Array of objects | ❌ Not present |
| `Facilitator` | ✅ String | ❌ Not present |
| `Environment Setting` | ✅ String | ❌ Not present |
| `Duration` | ✅ String | ❌ Not present |
| `Elements` | ❌ Empty array | ✅ Array of strings |


---

## React Component Examples

### Source Filter Dropdown

```tsx
function ActivitySourceFilter({ 
  value, 
  onChange 
}: { 
  value: ActivitySource; 
  onChange: (source: ActivitySource) => void;
}) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value as ActivitySource)}>
      <option value="all">All Activities</option>
      <option value="curated">Curated Only</option>
      <option value="generated">AI Generated Only</option>
    </select>
  );
}
```

### Activity Card with Source Badge

```tsx
function ActivityCard({ activity }: { activity: Activity }) {
  const isCurated = activity.source === "curated";
  
  return (
    <div className="activity-card">
      <div className="header">
        <h3>{activity.activity_name}</h3>
        <span className={`badge ${activity.source}`}>
          {isCurated ? "Curated" : "AI Generated"}
        </span>
      </div>
      
      <p>{activity.activity_data["Activity Description"]}</p>
      
      <div className="meta">
        <span>Age: {activity.age}</span>
        <span>Risk: {activity.risk_level}</span>
        <span>Duration: {activity.duration_pref}</span>
      </div>
      
      {/* Only show for curated activities */}
      {isCurated && activity.activity_data["Materials Required"] && (
        <div className="materials">
          <h4>Materials Required</h4>
          <ul>
            {(activity.activity_data as CuratedActivityData)["Materials Required"].map((m, i) => (
              <li key={i}>{m}</li>
            ))}
          </ul>
        </div>
      )}
      
      {isCurated && activity.activity_data["Safety Requirements"] && (
        <div className="safety">
          <h4>Safety Requirements</h4>
          <ul>
            {(activity.activity_data as CuratedActivityData)["Safety Requirements"].map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```


### CSS for Source Badges

```css
.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.badge.curated {
  background-color: #4CAF50;
  color: white;
}

.badge.generated {
  background-color: #2196F3;
  color: white;
}
```

---

## Helper Functions

```typescript
// Type guard to check if activity is curated
function isCuratedActivity(activity: Activity): boolean {
  return activity.source === "curated";
}

// Safe accessor for curated-only fields
function getMaterials(activity: Activity): string[] {
  if (activity.source === "curated") {
    return (activity.activity_data as CuratedActivityData)["Materials Required"] || [];
  }
  return [];
}

function getSafetyRequirements(activity: Activity): string[] {
  if (activity.source === "curated") {
    return (activity.activity_data as CuratedActivityData)["Safety Requirements"] || [];
  }
  return [];
}

function getFullInstructions(activity: Activity): string[] {
  if (activity.source === "curated") {
    return (activity.activity_data as CuratedActivityData)["Full Instructions"] || [];
  }
  return [];
}

// Get themes as array (activity_data.Themes is already an array)
function getThemesArray(activity: Activity): string[] {
  return activity.activity_data.Themes || [];
}
```

---

## Notes

1. **Database columns** (`themes`, `setting`, etc.) are duplicated in `activity_data` - use whichever is convenient
2. **`themes`** column is a comma-separated string, while `activity_data.Themes` is an array
3. **Generated activities** have `Elements` field populated, curated activities have it empty
4. **Check `source` field** before accessing curated-only fields like `Materials Required`
