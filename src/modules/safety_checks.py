import cv2
from ultralytics import YOLO

# Pre-trained YOLOv8 nano model (trained on the COCO dataset).
# COCO includes a "cell phone" class, which is what we use here.
# NOTE: COCO does NOT include a "seatbelt" class, so seatbelt detection
# is not possible with this pre-trained model alone. Real seatbelt
# detection would require training a custom YOLO model on a labeled
# seatbelt dataset (e.g. from Roboflow) - documented as a known
# limitation / future improvement for this module.
_model = None


def _get_model():
    global _model
    if _model is None:
        _model = YOLO("yolov8n.pt")  # auto-downloads on first run
    return _model


def analyze_safety_checks(video_path, sample_every_n_frames=5):
    """
    Analyzes a driving test video for phone usage.

    Args:
        video_path: path to the candidate's driving test video file
        sample_every_n_frames: only run YOLO every Nth frame to keep
            processing time reasonable (object detection is slower
            than the lightweight OpenCV/MediaPipe modules).

    Returns:
        dict summary with frame counts and a 0-20 safety score,
        matching the scoring scale used in the project's example report.
        Seatbelt fields are included but marked as not implemented.
    """
    model = _get_model()
    cap = cv2.VideoCapture(video_path)

    total_frames = 0
    analyzed_frames = 0
    phone_detected_frames = 0

    frame_index = 0
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        total_frames += 1
        frame_index += 1

        if frame_index % sample_every_n_frames != 0:
            continue

        analyzed_frames += 1
        results = model(frame, verbose=False)

        phone_found = False
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                class_name = model.names[class_id]
                if class_name == "cell phone":
                    phone_found = True
                    break
            if phone_found:
                break

        if phone_found:
            phone_detected_frames += 1

    cap.release()

    if analyzed_frames == 0:
        phone_ratio = 0
    else:
        phone_ratio = phone_detected_frames / analyzed_frames

    # Deduct from a max score of 20, matching the project's example report scale.
    # Phone usage is weighted heavily since it's a serious safety violation.
    penalty = phone_ratio * 20
    safety_score = max(0, round(20 - penalty))

    return {
        "total_frames": total_frames,
        "analyzed_frames": analyzed_frames,
        "phone_detected_frames": phone_detected_frames,
        "seatbelt_check": "not implemented - requires custom-trained model",
        "safety_score": safety_score,
    }


if __name__ == "__main__":
    # Quick manual test: run this file directly with a sample video path
    result = analyze_safety_checks("phone_test_video.mp4")
    print(result)

