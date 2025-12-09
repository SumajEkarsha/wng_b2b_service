from fastapi import FastAPI, Query
from typing import List, Optional
# from database import get_connection      
# from s3_service import read_bytes_from_s3
import base64
import boto3
from botocore.client import Config
import os


app = FastAPI(title="Activity Retrieval API")


def get_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")
    return psycopg2.connect(DATABASE_URL)

def read_bytes_from_s3(s3_path: str):
    """Read raw bytes (images, files)."""
    obj = s3.get_object(Bucket=AWS_S3_BUCKET, Key=s3_path)
    return obj["Body"].read()

# -------------------------------------------------------
# S3 Flashcard Loader
# -------------------------------------------------------
def fetch_flashcards_from_s3(activity_id: str) -> dict:
    """
    Returns flashcards as:
    {
        "step1": "base64String...",
        "step2": "base64String..."
    }
    """
    bucket = os.getenv("AWS_S3_BUCKET")
    s3 = boto3.client(
        "s3",
        region_name=os.getenv("AWS_REGION"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        config=Config(signature_version="s3v4")
    )

    prefix = f"master/selected_activities/{activity_id}/flashcards/"
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

    flashcards = {}

    if "Contents" not in response:
        return flashcards  

    for obj in response["Contents"]:
        key = obj["Key"]
        if key.endswith((".png", ".jpg", ".jpeg")):
            file_bytes = read_bytes_from_s3(key)
            step_name = key.split("/")[-1].split(".")[0]
            flashcards[step_name] = base64.b64encode(file_bytes).decode("utf-8")

    return flashcards


# -------------------------------------------------------
# DB Query Function With Themes Support
# -------------------------------------------------------
def query_activities(
    age: Optional[int],
    diagnosis: Optional[str],
    themes: Optional[List[str]],
):
    """
    Fetch activities filtered by:
    - age
    - diagnosis
    - themes (contains ANY of the themes)
    """

    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT activity_data
        FROM Activities
        WHERE 
            (%s IS NULL OR age = %s)
        AND (%s IS NULL OR diagnosis ILIKE %s)
    """

    params = [
        age, age,
        diagnosis, f"%{diagnosis}%" if diagnosis else None
    ]

    cur.execute(query, params)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    results = [r[0] for r in rows]

    # ---------- Filter by themes in Python ----------
    if themes:
        filtered = []
        for act in results:
            act_themes = act.get("Themes", [])
            act_themes = [t.lower() for t in act_themes] if isinstance(act_themes, list) else []

            for t in themes:
                if t.lower() in act_themes:
                    filtered.append(act)
                    break
        return filtered

    return results


# -------------------------------------------------------
# Main API Endpoint 
# -------------------------------------------------------
@app.get("/fetch-activities")
def fetch_activities_api(
    age: Optional[int] = Query(default=None),
    diagnosis: Optional[str] = Query(default=None),
    themes: Optional[str] = Query(default=None),
):
    """
    Fetch activities with optional filters.
    
    Example:
        /fetch-activities?age=8&diagnosis=ADHD&themes=Emotional Regulation,Motor Skills
    """

    theme_list = [t.strip() for t in themes.split(",")] if themes else []

    activities = query_activities(age, diagnosis, theme_list)

    final_output = []

    for act in activities:
        activity_id = act.get("Activity ID")
        flashcards = fetch_flashcards_from_s3(activity_id)

        formatted = {
            "Activity ID": act.get("Activity ID"),
            "Activity Name": act.get("Activity Name"),
            "Activity Description": act.get("Activity Description"),
            "Therapy Goal": act.get("Therapy Goal"),
            "Learning Goal": act.get("Learning Goal"),
            "Age": act.get("Age"),
            "Themes": act.get("Themes"),
            "Diagnosis": act.get("Diagnosis"),
            "Instructions": flashcards,
        }

        final_output.append(formatted)

    return {
        "filters": {
            "age": age,
            "diagnosis": diagnosis,
            "themes": theme_list
        },
        "count": len(final_output),
        "activities": final_output
    }
