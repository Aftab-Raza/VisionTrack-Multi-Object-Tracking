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


# ==========================================
# Polygon Zone Configuration
# ==========================================

# Coordinates are normalized between 0 and 1.
#
# Example:
# (0.30, 0.25)
# means:
# x = 30% of frame width
# y = 25% of frame height
#
# Using normalized coordinates allows the
# zone to work with different video resolutions.

ZONES = {

    "Restricted Zone": [

        (0.30, 0.25),
        (0.75, 0.25),
        (0.75, 0.80),
        (0.30, 0.80)

    ]

}


# Remove zone-tracking information for an
# object if it has disappeared for this many frames.

ZONE_TRACK_MAX_AGE = 150


# Maximum recent zone events stored in memory.

ZONE_EVENT_HISTORY_LIMIT = 50


# ==========================================
# Persistence Configuration
# ==========================================

# CSV event logging
ENABLE_CSV_LOGGING = True

EVENT_LOG_FILE = "logs/events.csv"


# Event snapshots
ENABLE_EVENT_SNAPSHOTS = True

SNAPSHOT_DIRECTORY = "outputs/snapshots"

SNAPSHOT_JPEG_QUALITY = 90


# Processed video recording
ENABLE_VIDEO_RECORDING = True

OUTPUT_VIDEO_FILE = "outputs/visiontrack_output.mp4"

# Used if source FPS cannot be determined
OUTPUT_VIDEO_FPS_FALLBACK = 25.0


# ==========================================
# Database Configuration
# ==========================================

ENABLE_DATABASE = True

DATABASE_PATH = "data/visiontrack.db"

# Writing every frame directly to disk can
# reduce FPS. Commit updates periodically.
DB_COMMIT_INTERVAL_FRAMES = 30


# ==========================================
# Tracker Backend Configuration
# ==========================================

# Available:
# "bytetrack"
# "custom"

TRACKER_MODE = "bytetrack"


# ==========================================
# Custom MOT Configuration
# ==========================================

# Minimum IoU required to associate an
# existing track with a new detection.
CUSTOM_IOU_THRESHOLD = 0.25


# A new track must be detected this many
# times before it becomes confirmed.
CUSTOM_MIN_HITS = 3


# Number of consecutive unmatched frames
# allowed before removing a track.
CUSTOM_MAX_MISSED = 20


TRACKER_MODE = "bytetrack"

CUSTOM_IOU_THRESHOLD = 0.25

CUSTOM_MIN_HITS = 3

CUSTOM_MAX_MISSED = 20

# ==========================================
# Benchmark Configuration
# ==========================================

ENABLE_BENCHMARKING = True

BENCHMARK_DIRECTORY = "outputs/benchmarks"

# Store frame-level measurements.
SAVE_FRAME_BENCHMARKS = True