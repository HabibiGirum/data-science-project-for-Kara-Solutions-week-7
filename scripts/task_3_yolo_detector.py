import cv2
import torch
import logging
import sqlite3
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class YOLOObjectDetector:
    def __init__(self, model_path="yolov5s.pt", db_path="detections.db"):
        """
        Initialize the YOLO object detector.
        :param model_path: Path to the YOLO model weights.
        :param db_path: Path to the SQLite database to store detection results.
        """
        self.model = self._load_yolo_model(model_path)
        self.db_path = db_path
        self._setup_database()

    def _load_yolo_model(self, model_path):
        """
        Load the YOLO model.
        :param model_path: Path to the YOLO model weights.
        :return: Loaded YOLO model.
        """
        try:
            model = torch.hub.load("ultralytics/yolov5", "custom", path=model_path)
            logging.info("YOLO model loaded successfully.")
            return model
        except Exception as e:
            logging.error(f"Failed to load YOLO model: {e}")
            raise

    def _setup_database(self):
        """
        Set up the SQLite database to store detection results.
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_path TEXT,
                    class_label TEXT,
                    confidence REAL,
                    x_min INTEGER,
                    y_min INTEGER,
                    x_max INTEGER,
                    y_max INTEGER
                )
                """
            )
            self.conn.commit()
            logging.info("Database setup completed.")
        except Exception as e:
            logging.error(f"Failed to set up database: {e}")
            raise

    def detect_objects(self, image_path):
        """
        Detect objects in an image using YOLO.
        :param image_path: Path to the input image.
        """
        try:
            image = cv2.imread(image_path)
            results = self.model(image)
            detections = results.xyxy[0].numpy()  # Extract detection results

            for detection in detections:
                x_min, y_min, x_max, y_max, confidence, class_id = detection
                class_label = self.model.names[int(class_id)]
                self._store_detection(image_path, class_label, confidence, x_min, y_min, x_max, y_max)
                logging.info(f"Detected {class_label} with confidence {confidence:.2f} in {image_path}")

        except Exception as e:
            logging.error(f"Error during object detection: {e}")

    def _store_detection(self, image_path, class_label, confidence, x_min, y_min, x_max, y_max):
        """
        Store detection results in the database.
        """
        try:
            self.cursor.execute(
                """
                INSERT INTO detections (image_path, class_label, confidence, x_min, y_min, x_max, y_max)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (image_path, class_label, confidence, x_min, y_min, x_max, y_max),
            )
            self.conn.commit()
            logging.info(f"Stored detection for {class_label} in database.")
        except Exception as e:
            logging.error(f"Failed to store detection in database: {e}")

    def close(self):
        """
        Close the database connection.
        """
        self.conn.close()
        logging.info("Database connection closed.")

