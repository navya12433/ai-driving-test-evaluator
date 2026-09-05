import cv2
import numpy as np
from ultralytics import YOLO

# Pre-trained YOLOv8 nano model (trained on the COCO dataset).
# COCO includes a "traffic light" class, but does NOT tell us the
# light's color or the vehicle's actual speed. Those are approximated
# below with basic HSV color analysis and frame-differencing motion
# detection - documented limitations, not a fully robust solution.
_model = None


def _get_model():
    global _model
    if _model is None:
        _model = YOLO("yolov8n.pt")  # auto-downloads on first run
    return _model


def _classify_light_color(frame, box):
    """
    Crops the detected traffic light region and checks whether red or
    green pixels dominate, using simple HSV color thresholding.
    Returns "red", "green", or None if inconclusive.
    """
    x1, y1, x2, y2 = map(int, box)
    crop = frame[y1:y2, x1:x2]
    if crop.size == 0:
        return None

    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)

    red_mask1 = cv2.inRange(hsv, (0, 100, 100), (10, 255, 255))
    red_mask2 = cv2.inRange(hsv, (160, 100, 100), (180, 255, 255))
    red_pixels = cv2.countNonZero(red_mask1) + cv2.countNonZero(red_mask2)

    green_mask = cv2.inRange(hsv, (40, 100, 100), (90, 255, 255))
    green_pixels = cv2.countNonZero(green_mask)

    if red_pixels < 5 and green_pixels < 5:
        return None  # not enough color signal either way

    return "red" if red_pixels > green_pixels else "green"


def _is_vehicle_moving(prev_frame, curr_frame, threshold=15.0):
    """
    Rough motion proxy: compares consecutive frames and measures
    average pixel difference. This is NOT real vehicle speed, just
    an approximation of whether the scene is changing significantly.
    """
    if prev_frame is None:
        return None

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

    diff = cv2.absdiff(prev_gray, curr_gray)
    return diff.mean() > threshold


def analyze_signal_compliance(video_path, sample_every_n_frames=5):
    """
    Analyzes a driving test video for red-light compliance.

    Args:
        video_path: path to the candidate's driving test video file
        sample_every_n_frames: only run YOLO every Nth frame to keep
            processing time reasonable.

    Returns:
        dict summary with frame counts and a 0-20 signal compliance
        score, matching the scoring scale used in the project's
        example report.
    """
    model = _get_model()
    cap = cv2.VideoCapture(video_path)

    total_frames = 0
    analyzed_frames = 0
    red_light_frames = 0
    violation_frames = 0

    prev_frame = None
    frame_index = 0

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        total_frames += 1
        frame_index += 1

        if frame_index % sample_every_n_frames != 0:
            prev_frame = frame
            continue

        analyzed_frames += 1
        results = model(frame, verbose=False)

        light_color = None
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                class_name = model.names[class_id]
                if class_name == "traffic light":
                    light_color = _classify_light_color(frame, box.xyxy[0])
                    if light_color:
                        break
            if light_color:
                break

        if light_color == "red":
            red_light_frames += 1
            moving = _is_vehicle_moving(prev_frame, frame)
            if moving:
                violation_frames += 1

        prev_frame = frame

    cap.release()

    if red_light_frames == 0:
        signal_compliance_score = 20  # no red lights encountered, nothing to penalize
    else:
        violation_ratio = violation_frames / red_light_frames
        penalty = violation_ratio * 20
        signal_compliance_score = max(0, round(20 - penalty))

    return {
        "total_frames": total_frames,
        "analyzed_frames": analyzed_frames,
        "red_light_frames": red_light_frames,
        "violation_frames": violation_frames,
        "signal_compliance_score": signal_compliance_score,
    }


if __name__ == "__main__":
    # Quick manual test: run this file directly with a sample video path
    result = analyze_signal_compliance("signal_test_video (2).mp4")
    print(result)
