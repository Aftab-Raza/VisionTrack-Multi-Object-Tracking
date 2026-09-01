# ==============================
# VisionTrack Configuration
# ==============================

MODEL_PATH = "yolo11n.pt"

CONFIDENCE_THRESHOLD = 0.35

TRACKER_CONFIG = "bytetrack.yaml"

# 0 means default webcam
VIDEO_SOURCE = 0

# Number of trajectory points retained per object
MAX_TRAJECTORY_LENGTH = 50

# Minimum pixel movement used for direction detection
MOVEMENT_THRESHOLD = 3