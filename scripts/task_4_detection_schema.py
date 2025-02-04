from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import sqlite3

# Define Pydantic schemas
class DetectionSchema(BaseModel):
    id: int
    image_path: str
    class_label: str
    confidence: float
    x_min: int
    y_min: int
    x_max: int
    y_max: int

# Initialize FastAPI app
app = FastAPI()

# Database configuration
DATABASE_PATH = "detections.db"

def get_db_connection():
    """
    Get a connection to the SQLite database.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/detections/", response_model=List[DetectionSchema])
def get_all_detections():
    """
    Retrieve all detections from the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM detections")
    detections = cursor.fetchall()
    conn.close()
    return detections

@app.get("/detections/{detection_id}", response_model=DetectionSchema)
def get_detection_by_id(detection_id: int):
    """
    Retrieve a specific detection by its ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM detections WHERE id = ?", (detection_id,))
    detection = cursor.fetchone()
    conn.close()
    if detection is None:
        raise HTTPException(status_code=404, detail="Detection not found")
    return detection

@app.post("/detections/", response_model=DetectionSchema)
def create_detection(detection: DetectionSchema):
    """
    Create a new detection entry in the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO detections (image_path, class_label, confidence, x_min, y_min, x_max, y_max)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            detection.image_path,
            detection.class_label,
            detection.confidence,
            detection.x_min,
            detection.y_min,
            detection.x_max,
            detection.y_max,
        ),
    )
    conn.commit()
    detection_id = cursor.lastrowid
    conn.close()
    return {**detection.dict(), "id": detection_id}

