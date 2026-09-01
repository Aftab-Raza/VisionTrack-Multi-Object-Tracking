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


# ==============================
# Line Crossing Configuration
# ==============================

# Horizontal counting line position.
# 0.55 means 55% down the video frame.
LINE_POSITION_RATIO = 0.55

# Dead-zone around the line to prevent
# small tracking fluctuations from creating false crossings.
LINE_MARGIN = 10

# Prevent the same object from being counted repeatedly
# due to tracking jitter.
CROSSING_COOLDOWN_FRAMES = 20

# Remove very old track IDs from line-counter memory
TRACK_MEMORY_MAX_AGE = 300