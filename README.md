# AI-Based Driving Test Evaluation System

An automated driving test evaluation system that analyzes a candidate's driving test video and generates a scored report — reducing manual evaluation and providing a consistent, objective assessment.

## How it works

1. A candidate's driving test video is uploaded through the web interface.
2. The Flask backend processes the video frame-by-frame using five independent AI/CV modules.
3. Each module returns a score out of 20, covering a different aspect of driving performance.
4. Scores are combined into a total out of 100, with a PASS/FAIL result.
5. Every evaluation is saved to a database, viewable on the History page.

## Example output

```
Driving Test Evaluation
Lane Discipline       11/20
Traffic Rules         20/20
Safety                20/20
Driver Attention       0/20
Unsafe Behavior        19/20
Total Score:           70/100
Result: PASS
```

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Flask |
| AI / Computer Vision | OpenCV, MediaPipe, YOLOv8 (Ultralytics) |
| Database | SQLite |

## Project structure

```
ai-driving-test-evaluator/
├── frontend/
│   ├── index.html          # Upload + evaluation page
│   ├── history.html        # Past evaluations page
│   ├── css/style.css
│   └── js/
│       ├── script.js
│       └── history.js
├── src/
│   └── modules/
│       ├── driver_attention.py
│       ├── lane_discipline.py
│       ├── safety_checks.py
│       ├── signal_compliance.py
│       └── unsafe_behavior.py
├── app.py                  # Flask API
├── database.py             # SQLite storage
├── requirements.txt
└── README.md
```

## Modules

### Driver Attention (`src/modules/driver_attention.py`)
Uses MediaPipe Face Mesh to detect facial landmarks and estimate:
- Eye closure (drowsiness), via Eye Aspect Ratio
- Head direction (looking away from the road)

### Lane Discipline (`src/modules/lane_discipline.py`)
Classical computer vision using OpenCV: Canny edge detection + Hough Line Transform to detect lane markings and measure how centered the vehicle stays within its lane.

### Safety Checks (`src/modules/safety_checks.py`)
Pre-trained YOLOv8 object detection, used to detect phone usage while driving.

### Signal Compliance (`src/modules/signal_compliance.py`)
Pre-trained YOLOv8 to detect traffic lights, combined with HSV color analysis to classify red/green, and frame-differencing to approximate whether the vehicle was moving through a red light.

### Unsafe Behavior (`src/modules/unsafe_behavior.py`)
Frame-to-frame motion analysis. Flags statistically unusual spikes in visual motion (more than 2.5 standard deviations above the video's average) as potential harsh braking, acceleration, or swerving events.

## Known limitations

This project makes deliberate, documented simplifications where full production-grade solutions would require resources beyond the scope of a student project:

- **Seatbelt detection is not implemented.** The pre-trained YOLOv8 model (trained on the COCO dataset) has no "seatbelt" class. Detecting seatbelts would require training a custom model on a labeled seatbelt dataset.
- **Traffic light color detection uses basic HSV thresholding**, which performs well in daytime conditions but is less reliable at night or in glare/reflective conditions, where ambient lighting can be misread as signal color.
- **"Unsafe behavior" and "vehicle moving" detection are approximated using frame-to-frame visual motion**, not real accelerometer, GPS, or speed-sensor data. This is a reasonable proxy but can be affected by camera shake or other objects moving through frame.
- **Lane detection accuracy depends on video quality.** Classical edge/line detection performs best on clear, well-lit footage with visible lane markings; heavy fog, obstruction (e.g. a large vehicle ahead), or worn road markings reduce detection confidence — in these cases, the module only scores frames it is confident about, rather than guessing.

These limitations are intentional engineering trade-offs, not oversights, and are documented here for transparency.

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the backend:
   ```
   python app.py
   ```
4. Open `frontend/index.html` in a browser

## Team

Built by [team name] as a final-year project.