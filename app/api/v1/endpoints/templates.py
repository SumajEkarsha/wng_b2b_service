from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import pandas as pd
from io import BytesIO

from app.core.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)

router = APIRouter()

@router.get("/staff-template")
async def download_staff_template():
    """Download Excel template for staff data upload"""
    logger.info("Staff template download requested")
    
    # Create sample data
    data = {
        'first_name': ['John', 'Jane', 'Robert'],
        'last_name': ['Doe', 'Smith', 'Johnson'],
        'email': ['john.doe@school.edu', 'jane.smith@school.edu', 'robert.johnson@school.edu'],
        'role': ['teacher', 'counsellor', 'principal'],
        'phone': ['9876543210', '9876543211', '9876543212'],
        'subject': ['Mathematics', '', '']  # Only for teachers
    }
    
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Staff')
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=staff_template.xlsx'}
    )

@router.get("/students-template")
async def download_students_template():
    """Download Excel template for students and parents data upload"""
    logger.info("Students template download requested")
    
    # Create sample data
    data = {
        'first_name': ['Alice', 'Bob'],
        'last_name': ['Johnson', 'Williams'],
        'date_of_birth': ['2010-05-15', '2011-08-22'],
        'grade': ['8', '7'],
        'gender': ['Female', 'Male'],
        'parent_name': ['Mary Johnson', 'Robert Williams'],
        'parent_email': ['mary.j@email.com', 'robert.w@email.com'],
        'parent_phone': ['5551234567', '5559876543'],
        'parent_relationship': ['Mother', 'Father']
    }
    
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Students')
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=students_template.xlsx'}
    )

@router.get("/classes-template")
async def download_classes_template():
    """Download Excel template for classes data upload"""
    logger.info("Classes template download requested")
    
    # Create sample data
    data = {
        'class_name': ['Math 101', 'English 201'],
        'grade': ['8', '9'],
        'section': ['A', 'B'],
        'teacher_email': ['john.doe@school.edu', 'jane.smith@school.edu'],
        'subject': ['Mathematics', 'English'],
        'room_number': ['101', '202']
    }
    
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Classes')
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=classes_template.xlsx'}
    )
