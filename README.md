# VisionTrack

VisionTrack is a real-time multi-object detection and tracking system built using Python, OpenCV, and YOLO. The project detects multiple objects in video streams, assigns persistent IDs to detected objects, tracks their movement across frames, and provides trajectory-based analytics.

## Features

* Real-time multi-object detection
* Unique ID assignment for tracked objects
* Object trajectory visualization
* Video file processing
* Modular tracking architecture
* Processed video output generation
* Logging support
* Object movement analytics
* Extendable architecture for speed estimation, object counting, and zone monitoring


## Tech Stack

* Python
* OpenCV
* YOLO
* Ultralytics
* NumPy
* Multi-Object Tracking
* Computer Vision

## Project Structure

```text
VisionTrack/
│
├── app.py
├── config.py
├── requirements.txt
│
├── core/
│   ├── __init__.py
│   ├── video_source.py
│   └── tracker.py
│
├── analytics/
│   ├── __init__.py
│   └── trajectory.py
│
├── utils/
│   ├── __init__.py
│   └── drawing.py
│
├── videos/
├── outputs/
├── logs/
└── models/
```

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/VisionTrack.git
```

Move into the project directory:

```bash
cd VisionTrack
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Place an input video inside the `videos/` directory.

Run the application:

```bash
python app.py
```

The processed tracking results will be stored inside the `outputs/` directory.

## How It Works

VisionTrack follows a computer vision pipeline:

```text
Video Input
     ↓
Frame Extraction
     ↓
YOLO Object Detection
     ↓
Multi-Object Tracker
     ↓
Unique Object IDs
     ↓
Trajectory Analysis
     ↓
Bounding Box + Track Visualization
     ↓
Processed Video Output
```

Each incoming video frame is processed by the object detector. Detected objects are passed to the tracking module, which maintains their identities across consecutive frames.

The trajectory module stores the movement history of each tracked object and can be used for further analytics.

## Planned Features

* Object counting
* Line-crossing detection
* Entry and exit monitoring
* Region-of-interest monitoring
* Object speed estimation
* Direction analysis
* Real-time webcam support
* Tracking statistics dashboard
* CSV analytics export

## Applications

VisionTrack can be extended for:

* Traffic monitoring
* Crowd analytics
* CCTV surveillance
* Vehicle tracking
* Pedestrian tracking
* Smart city systems
* Retail analytics
* Industrial monitoring

## Author

Aftab Raza


