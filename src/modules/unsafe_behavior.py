import cv2
import numpy as np


def _frame_motion(prev_gray, curr_gray):
    """Average pixel difference between two consecutive grayscale frames."""
    diff = cv2.absdiff(prev_gray, curr_gray)
    return diff.mean()


def analyze_unsafe_behavior(video_path, sample_every_n_frames=3, spike_std_multiplier=2.5):
    """
    Analyzes a driving test video for sudden/unsafe driving behavior.

    Approach: measures frame-to-frame visual motion as a proxy for how
    abruptly the vehicle's speed or direction is changing. A sudden
    spike in this motion signal (well above the video's own average)
    is flagged as a potential harsh braking, sudden acceleration, or
    abrupt swerve event.

    LIMITATION: this is a visual approximation, not real accelerometer
    or speed-sensor data. It can be fooled by camera shake, other fast
    moving objects entering frame, or lighting changes - documented as
    a known simplification for this student project.

    Args:
        video_path: path to the candidate's driving test video file
        sample_every_n_frames: only measure motion every Nth frame
        spike_std_multiplier: how many standard deviations above the
            video's average motion counts as a "spike" (higher = stricter)

    Returns:
        dict summary with frame counts and a 0-20 unsafe behavior
        score, matching the scoring scale used in the project's
        example report.
    """
    cap = cv2.VideoCapture(video_path)

    total_frames = 0
    analyzed_frames = 0
    motion_values = []

    prev_gray = None
    frame_index = 0

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        total_frames += 1
        frame_index += 1

        if frame_index % sample_every_n_frames != 0:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev_gray is not None:
            analyzed_frames += 1
            motion_values.append(_frame_motion(prev_gray, gray))

        prev_gray = gray

    cap.release()

    if len(motion_values) < 2:
        return {
            "total_frames": total_frames,
            "analyzed_frames": analyzed_frames,
            "unsafe_event_frames": 0,
            "unsafe_behavior_score": 20,
        }

    motion_array = np.array(motion_values)
    mean_motion = motion_array.mean()
    std_motion = motion_array.std()

    spike_threshold = mean_motion + (spike_std_multiplier * std_motion)
    unsafe_event_frames = int(np.sum(motion_array > spike_threshold))

    spike_ratio = unsafe_event_frames / len(motion_array)

    # Deduct from a max score of 20, matching the project's example report scale.
    # Multiplied up since even a few genuine harsh events should meaningfully
    # affect the score.
    penalty = min(20, spike_ratio * 100)
    unsafe_behavior_score = max(0, round(20 - penalty))

    return {
        "total_frames": total_frames,
        "analyzed_frames": analyzed_frames,
        "unsafe_event_frames": unsafe_event_frames,
        "unsafe_behavior_score": unsafe_behavior_score,
    }


if __name__ == "__main__":
    # Quick manual test: run this file directly with a sample video path
    result = analyze_unsafe_behavior("sample_road_video.mp4")
    print(result)