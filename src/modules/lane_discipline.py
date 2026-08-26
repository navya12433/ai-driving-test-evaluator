import cv2
import numpy as np


def _region_of_interest(edges):
    """Mask out everything except the lower-middle 'road' region of the frame."""
    height, width = edges.shape
    mask = np.zeros_like(edges)

    # Trapezoid roughly covering the road ahead, ignoring sky/dashboard
    polygon = np.array([[
        (int(width * 0.1), int(height * 0.85)),
        (int(width * 0.4), int(height * 0.55)),
        (int(width * 0.6), int(height * 0.55)),
        (int(width * 0.9), int(height * 0.85)),
    ]], dtype=np.int32)

    cv2.fillPoly(mask, polygon, 255)
    return cv2.bitwise_and(edges, mask)


def _detect_lane_lines(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 100, 200)
    roi = _region_of_interest(edges)

    lines = cv2.HoughLinesP(

        roi, rho=2, theta=np.pi / 180, threshold=80,
        minLineLength=80, maxLineGap=50
    )
    

    # Different OpenCV versions return slightly different shapes.
    # Normalize to a flat (N, 4) array of [x1, y1, x2, y2] rows.
    if lines is not None:
        lines = lines.reshape(-1, 4)

    return lines


def _classify_frame(lines, frame_width):
    """
    Splits detected lines into left/right lane candidates based on slope,
    then checks whether the vehicle appears centered between them.
    Returns True if the frame looks like the vehicle is within its lane.
    """
    if lines is None:
        return None  # couldn't detect lanes in this frame, skip it

    left_x = []
    right_x = []
    frame_center = frame_width / 2

    for line in lines:
        x1, y1, x2, y2 = line
        if x2 == x1:
            continue  # vertical line, skip (avoid divide by zero)

        slope = (y2 - y1) / (x2 - x1)

        if slope < -0.5:
            left_x.extend([x1, x2])
        elif slope > 0.5:
            right_x.extend([x1, x2])

    if not left_x or not right_x:
        return None  # only found one side, not enough info

    left_edge = max(left_x)
    right_edge = min(right_x)
    lane_center = (left_edge + right_edge) / 2

    offset = abs(lane_center - frame_center)
    lane_width = right_edge - left_edge
    if lane_width <= 0:
        return None

    offset_ratio = offset / lane_width

    # Within 15% of lane width from center counts as "in lane"
    return offset_ratio < 0.15


def analyze_lane_discipline(video_path):
    """
    Analyzes a driving test video for lane discipline.

    Args:
        video_path: path to the candidate's driving test video file

    Returns:
        dict summary with frame counts and a 0-20 lane discipline score,
        matching the scoring scale used in the project's example report.
    """
    cap = cv2.VideoCapture(video_path)

    total_frames = 0
    lane_detected_frames = 0
    in_lane_frames = 0
    out_of_lane_frames = 0

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        total_frames += 1
        h, w, _ = frame.shape

        lines = _detect_lane_lines(frame)
        in_lane = _classify_frame(lines, w)

        if in_lane is not None:
            lane_detected_frames += 1
            if in_lane:
                in_lane_frames += 1
            else:
                out_of_lane_frames += 1

    cap.release()

    if lane_detected_frames == 0:
        return {
            "total_frames": total_frames,
            "lane_detected_frames": 0,
            "in_lane_frames": 0,
            "out_of_lane_frames": 0,
            "lane_discipline_score": 0,
        }

    out_of_lane_ratio = out_of_lane_frames / lane_detected_frames

    # Deduct from a max score of 20, matching the project's example report scale
    penalty = out_of_lane_ratio * 20
    lane_discipline_score = max(0, round(20 - penalty))

    return {
        "total_frames": total_frames,
        "lane_detected_frames": lane_detected_frames,
        "in_lane_frames": in_lane_frames,
        "out_of_lane_frames": out_of_lane_frames,
        "lane_discipline_score": lane_discipline_score,
    }


def debug_visualize(video_path, output_path="debug_output.mp4"):
    """
    Saves a copy of the video with detected lane lines and the
    region-of-interest drawn on top, for visual debugging.
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 20
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        lines = _detect_lane_lines(frame)

        if lines is not None:
            for x1, y1, x2, y2 in lines:
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

        polygon = np.array([[
            (int(w * 0.1), h),
            (int(w * 0.4), int(h * 0.6)),
            (int(w * 0.6), int(h * 0.6)),
            (int(w * 0.9), h),
        ]], dtype=np.int32)
        cv2.polylines(frame, polygon, True, (255, 0, 0), 2)

        out.write(frame)

    cap.release()
    out.release()
    print(f"Saved debug video to {output_path}")


if __name__ == "__main__":
    result = analyze_lane_discipline("sample_road_video.mp4")
    print(result)