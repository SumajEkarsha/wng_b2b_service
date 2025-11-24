from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from app.models.student import Gender
from app.models.assessment import QuestionType

# Question and Answer Option schemas
class AnswerOption(BaseModel):
    option_id: str = Field(..., description="Unique identifier for the answer option")
    text: str = Field(..., description="Answer option text")
    value: Optional[float] = Field(default=None, description="Numeric value for scoring")
    
    class Config:
        json_schema_extra = {
            "example": {
                "option_id": "opt1",
                "text": "Not at all",
                "value": 0
            }
        }

class Question(BaseModel):
    question_id: str = Field(..., description="Unique identifier for the question")
    question_text: str = Field(..., description="Question text")
    question_type: QuestionType = Field(..., description="Type of question")
    required: bool = Field(default=True, description="Whether the question is required")
    answer_options: Optional[List[AnswerOption]] = Field(default=None, description="Available answer options")
    min_value: Optional[float] = Field(default=None, description="Minimum value for rating scales")
    max_value: Optional[float] = Field(default=None, description="Maximum value for rating scales")
    category: Optional[str] = Field(default=None, description="Question category for scoring")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "q1",
                "question_text": "How often do you feel sad?",
                "question_type": "rating_scale",
                "required": True,
                "min_value": 0,
                "max_value": 5,
                "category": "depression"
            }
        }

# Assessment Template schemas
class AssessmentTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Template name")
    description: Optional[str] = Field(default=None, description="Template description")
    category: Optional[str] = Field(default=None, description="Assessment category")
    questions: List[Question] = Field(..., description="List of questions")
    scoring_rules: Optional[Dict[str, Any]] = Field(default=None, description="Rules for calculating scores")
    created_by: UUID = Field(..., description="ID of the user creating the template")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "PHQ-9 Depression Screening",
                "description": "Patient Health Questionnaire - 9 items for adolescent depression screening. Widely validated assessment tool.",
                "category": "depression",
                "created_by": "b503fbc2-0e51-4996-9fcc-9d83fddc3760",
                "questions": [
                    {
                        "question_id": "q1",
                        "question_text": "Over the last 2 weeks, how often have you had little interest or pleasure in doing things?",
                        "question_type": "rating_scale",
                        "required": True,
                        "min_value": 0,
                        "max_value": 3,
                        "category": "depression",
                        "answer_options": [
                            {"option_id": "opt0", "text": "Not at all", "value": 0},
                            {"option_id": "opt1", "text": "Several days", "value": 1},
                            {"option_id": "opt2", "text": "More than half the days", "value": 2},
                            {"option_id": "opt3", "text": "Nearly every day", "value": 3}
                        ]
                    },
                    {
                        "question_id": "q2",
                        "question_text": "Over the last 2 weeks, how often have you felt down, depressed, or hopeless?",
                        "question_type": "rating_scale",
                        "required": True,
                        "min_value": 0,
                        "max_value": 3,
                        "category": "depression",
                        "answer_options": [
                            {"option_id": "opt0", "text": "Not at all", "value": 0},
                            {"option_id": "opt1", "text": "Several days", "value": 1},
                            {"option_id": "opt2", "text": "More than half the days", "value": 2},
                            {"option_id": "opt3", "text": "Nearly every day", "value": 3}
                        ]
                    },
                    {
                        "question_id": "q3",
                        "question_text": "Over the last 2 weeks, have you had trouble falling or staying asleep, or sleeping too much?",
                        "question_type": "rating_scale",
                        "required": True,
                        "min_value": 0,
                        "max_value": 3,
                        "category": "depression"
                    }
                ],
                "scoring_rules": {
                    "total_score": "sum_all",
                    "max_score": 27,
                    "severity_ranges": {
                        "minimal": [0, 4],
                        "mild": [5, 9],
                        "moderate": [10, 14],
                        "moderately_severe": [15, 19],
                        "severe": [20, 27]
                    },
                    "clinical_action": {
                        "0-4": "Monitor, may not require treatment",
                        "5-9": "Use clinical judgment about treatment",
                        "10-14": "Treatment recommended",
                        "15-19": "Immediate treatment, close monitoring",
                        "20-27": "Immediate treatment, potentially psychiatric referral"
                    }
                }
            }
        }

class AssessmentTemplateUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None)
    questions: Optional[List[Question]] = Field(default=None)
    scoring_rules: Optional[Dict[str, Any]] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)

class AssessmentTemplateResponse(BaseModel):
    template_id: UUID
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    questions: List[Dict[str, Any]]
    scoring_rules: Optional[Dict[str, Any]] = None
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

# Student Response schemas
class StudentResponseCreate(BaseModel):
    question_id: str = Field(..., description="Question ID from the template")
    answer: Any = Field(..., description="Student's answer")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "q1",
                "answer": 2
            }
        }

class StudentResponseData(BaseModel):
    response_id: UUID
    question_id: str
    question_text: str
    answer: Any
    score: Optional[float] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Assessment schemas
class AssessmentCreate(BaseModel):
    template_id: Optional[UUID] = Field(default=None, description="ID of the assessment template to use (optional if questions provided)")
    school_id: UUID = Field(..., description="ID of the school")
    class_id: Optional[UUID] = Field(default=None, description="ID of the class (optional)")
    title: Optional[str] = Field(default=None, max_length=200, description="Optional title for this assessment")
    description: Optional[str] = Field(default=None, description="Assessment description")
    category: Optional[str] = Field(default=None, description="Assessment category")
    questions: Optional[List[Question]] = Field(default=None, description="Questions for the assessment (if not using template)")
    created_by: UUID = Field(..., description="ID of the user creating the assessment")
    notes: Optional[str] = Field(default=None, description="Additional notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "template_id": "123e4567-e89b-12d3-a456-426614174060",
                "school_id": "123e4567-e89b-12d3-a456-426614174001",
                "class_id": "123e4567-e89b-12d3-a456-426614174005",
                "title": "Mid-term Depression Screening - Class 5A",
                "created_by": "123e4567-e89b-12d3-a456-426614174020",
                "notes": "Assessment for entire class"
            }
        }

class AssessmentSubmit(BaseModel):
    assessment_id: UUID = Field(..., description="ID of the assessment")
    student_id: UUID = Field(..., description="ID of the student taking the assessment")
    responses: List[StudentResponseCreate] = Field(..., description="List of student responses")
    notes: Optional[str] = Field(default=None, description="Additional notes for this student's submission")
    
    class Config:
        json_schema_extra = {
            "example": {
                "assessment_id": "56aa6a8a-9d4c-403d-9f55-d37673436834",
                "student_id": "123e4567-e89b-12d3-a456-426614174003",
                "responses": [
                    {"question_id": "q1", "answer": 2},
                    {"question_id": "q2", "answer": 3},
                    {"question_id": "q3", "answer": 1}
                ],
                "notes": "Student appeared tired during assessment"
            }
        }

class StudentInfo(BaseModel):
    student_id: UUID
    first_name: str
    last_name: str
    gender: Optional[Gender] = None

    class Config:
        from_attributes = True

class CreatorInfo(BaseModel):
    user_id: UUID
    display_name: str
    role: str

    class Config:
        from_attributes = True

class TemplateInfo(BaseModel):
    template_id: UUID
    name: str
    category: Optional[str] = None
    
    class Config:
        from_attributes = True

class ClassInfo(BaseModel):
    class_id: UUID
    name: str
    grade_level: Optional[str] = None
    
    class Config:
        from_attributes = True

class AssessmentListResponse(BaseModel):
    """Simple assessment info for listing"""
    assessment_id: UUID
    template_id: UUID
    template_name: str
    school_id: UUID
    class_id: Optional[UUID] = None
    class_name: Optional[str] = None
    title: Optional[str] = None
    category: Optional[str] = None
    created_by: UUID
    created_at: datetime
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "assessment_id": "56aa6a8a-9d4c-403d-9f55-d37673436834",
                "template_id": "b503fbc2-0e51-4996-9fcc-9d83fddc3760",
                "template_name": "PHQ-9 Depression Screening",
                "school_id": "614077c0-9cde-4955-a384-5a0d0a1a1ef5",
                "class_id": "8f3c4567-e89b-12d3-a456-426614174033",
                "class_name": "Grade 8-A",
                "title": "Q1 Depression Screening - Grade 8A",
                "category": "depression",
                "created_by": "123e4567-e89b-12d3-a456-426614174021",
                "created_at": "2024-10-24T15:30:00Z",
                "notes": "First quarter mental health screening"
            }
        }

class StudentAssessmentResult(BaseModel):
    """Individual student's result for an assessment"""
    student_id: UUID
    student_name: str
    responses: List[StudentResponseData]
    total_score: Optional[float] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "student_id": "123e4567-e89b-12d3-a456-426614174007",
                "student_name": "Ethan Lopez",
                "responses": [
                    {
                        "response_id": "abc123-def456-ghi789",
                        "question_id": "q1",
                        "question_text": "Little interest or pleasure in doing things",
                        "answer": 3,
                        "score": 3.0,
                        "completed_at": "2024-10-24T15:45:00Z",
                        "created_at": "2024-10-24T15:45:00Z"
                    },
                    {
                        "response_id": "def456-ghi789-jkl012",
                        "question_id": "q2",
                        "question_text": "Feeling down, depressed, or hopeless",
                        "answer": 3,
                        "score": 3.0,
                        "completed_at": "2024-10-24T15:45:00Z",
                        "created_at": "2024-10-24T15:45:00Z"
                    }
                ],
                "total_score": 11.0,
                "completed_at": "2024-10-24T15:45:00Z"
            }
        }

class AssessmentResponse(BaseModel):
    """Full assessment details with all student results"""
    assessment_id: UUID
    template_id: UUID
    template: Optional[TemplateInfo] = None
    template_name: Optional[str] = None
    school_id: UUID
    class_id: Optional[UUID] = None
    class_obj: Optional[ClassInfo] = None
    class_name: Optional[str] = None
    title: Optional[str] = None
    category: Optional[str] = None
    created_by: UUID
    creator: CreatorInfo
    notes: Optional[str] = None
    created_at: datetime
    student_results: List[StudentAssessmentResult] = []

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "assessment_id": "56aa6a8a-9d4c-403d-9f55-d37673436834",
                "template_id": "b503fbc2-0e51-4996-9fcc-9d83fddc3760",
                "template": {
                    "template_id": "b503fbc2-0e51-4996-9fcc-9d83fddc3760",
                    "name": "PHQ-9 Depression Screening",
                    "category": "depression"
                },
                "school_id": "614077c0-9cde-4955-a384-5a0d0a1a1ef5",
                "class_id": "8f3c4567-e89b-12d3-a456-426614174033",
                "class_obj": {
                    "class_id": "8f3c4567-e89b-12d3-a456-426614174033",
                    "name": "Grade 8-A",
                    "grade_level": "8"
                },
                "title": "Q1 Depression Screening - Grade 8A",
                "created_by": "123e4567-e89b-12d3-a456-426614174021",
                "creator": {
                    "user_id": "123e4567-e89b-12d3-a456-426614174021",
                    "display_name": "Dr. David Chen",
                    "role": "counsellor"
                },
                "notes": "First quarter screening",
                "created_at": "2024-10-24T15:30:00Z",
                "student_results": [
                    {
                        "student_id": "123e4567-e89b-12d3-a456-426614174007",
                        "student_name": "Ethan Lopez",
                        "responses": [
                            {
                                "response_id": "abc123-def456",
                                "question_id": "q1",
                                "question_text": "Little interest or pleasure in doing things",
                                "answer": 3,
                                "score": 3.0,
                                "completed_at": "2024-10-24T15:45:00Z",
                                "created_at": "2024-10-24T15:45:00Z"
                            }
                        ],
                        "total_score": 11.0,
                        "completed_at": "2024-10-24T15:45:00Z"
                    }
                ]
            }
        }
