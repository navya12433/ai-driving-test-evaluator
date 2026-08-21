import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import math

# Landmark indices for left eye (top, bottom, left corner, right corner)
LEFT_EYE = [159, 145, 33, 133]

# Landmark indices for head direction
NOSE_TIP = 1
LEFT_FACE = 234
RIGHT_FACE = 454

EAR_THRESHOLD = 0.2
DIRECTION_THRESHOLD = 0.15


def _eye_aspect_ratio(landmarks, frame_w, frame_h):
    def pt(idx):
        lm = landmarks[idx]
        return (lm.x * frame_w, lm.y * frame_h)

    top = pt(LEFT_EYE[0])
    bottom = pt(LEFT_EYE[1])
    left = pt(LEFT_EYE[2])
    right = pt(LEFT_EYE[3])

    vertical = math.dist(top, bottom)
    horizontal = math.dist(left, right)

    return vertical / horizontal


def _head_direction(landmarks, frame_w):
    nose_x = landmarks[NOSE_TIP].x * frame_w
    left_x = landmarks[LEFT_FACE].x * frame_w
    right_x = landmarks[RIGHT_FACE].x * frame_w

    face_center = (left_x + right_x) / 2
    offset = nose_x - face_center
    face_width = right_x - left_x

    ratio = offset / face_width

    if ratio > DIRECTION_THRESHOLD:
        return "left"
    elif ratio < -DIRECTION_THRESHOLD:
        return "right"
    else:
        return "forward"


def analyze_driver_attention(video_path, model_path="face_landmarker.task"):
    """
    Analyzes a driving test video for driver attention.

    Args:
        video_path: path to the candidate's driving test video file
        model_path: path to the MediaPipe face_landmarker.task model file

    Returns:
        dict summary with frame counts and a 0-20 attention score,
        matching the scoring scale used in the project's example report.
    """
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.FaceLandmarkerOptions(base_options=base_options, num_faces=1)
    detector = vision.FaceLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(video_path)

    total_frames = 0
    face_detected_frames = 0
    drowsy_frames = 0
    looked_away_frames = 0

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        total_frames += 1
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = detector.detect(mp_image)

        if result.face_landmarks:
            face_detected_frames += 1
            landmarks = result.face_landmarks[0]

            ear = _eye_aspect_ratio(landmarks, w, h)
            if ear < EAR_THRESHOLD:
                drowsy_frames += 1

            direction = _head_direction(landmarks, w)
            if direction != "forward":
                looked_away_frames += 1

    cap.release()

    if face_detected_frames == 0:
        return {
            "total_frames": total_frames,
            "face_detected_frames": 0,
            "drowsy_frames": 0,
            "looked_away_frames": 0,
            "attention_score": 0,
        }

    drowsy_ratio = drowsy_frames / face_detected_frames
    looked_away_ratio = looked_away_frames / face_detected_frames

    # Deduct from a max score of 20, matching the project's example report scale
    penalty = (drowsy_ratio * 12) + (looked_away_ratio * 8)
    attention_score = max(0, round(20 - penalty))

    return {
        "total_frames": total_frames,
        "face_detected_frames": face_detected_frames,
        "drowsy_frames": drowsy_frames,
        "looked_away_frames": looked_away_frames,
        "attention_score": attention_score,
    }


if __name__ == "__main__":
    # Quick manual test: run this file directly with a sample video path
    result = analyze_driver_attention("sample_test_video.mp4")
    print(result)
