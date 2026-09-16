from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import uuid

sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'modules'))
from driver_attention import analyze_driver_attention
from lane_discipline import analyze_lane_discipline
from safety_checks import analyze_safety_checks
from signal_compliance import analyze_signal_compliance
from unsafe_behavior import analyze_unsafe_behavior

from database import init_db, save_evaluation, get_all_evaluations

app = Flask(__name__)
CORS(app)

init_db()

@app.route('/evaluate', methods=['POST'])
def evaluate():
    video = request.files.get('video')
    if not video:
        return jsonify({"error": "No video uploaded"}), 400

    video_path = f'uploaded_{uuid.uuid4().hex}.mp4'
    video.save(video_path)

    model_path = os.path.join('src', 'modules', 'face_landmarker.task')
    attention_result = analyze_driver_attention(video_path, model_path)

    lane_result = analyze_lane_discipline(video_path)

    safety_result = analyze_safety_checks(video_path)

    signal_result = analyze_signal_compliance(video_path)

    unsafe_result = analyze_unsafe_behavior(video_path)

    total_score = (
        attention_result["attention_score"]
        + lane_result["lane_discipline_score"]
        + safety_result["safety_score"]
        + signal_result["signal_compliance_score"]
        + unsafe_result["unsafe_behavior_score"]
    )
    result_label = "PASS" if total_score >= 50 else "FAIL"

    try:
        save_evaluation(
            filename=video.filename,
            attention_score=attention_result["attention_score"],
            lane_score=lane_result["lane_discipline_score"],
            safety_score=safety_result["safety_score"],
            signal_score=signal_result["signal_compliance_score"],
            unsafe_score=unsafe_result["unsafe_behavior_score"],
            total_score=total_score,
            result=result_label
        )
        print("Evaluation saved to database successfully.")
    except Exception as e:
        print("FAILED TO SAVE TO DATABASE:", e)

    return jsonify({
        "driver_attention": attention_result,
        "lane_discipline": lane_result,
        "safety_checks": safety_result,
        "signal_compliance": signal_result,
        "unsafe_behavior": unsafe_result,
        "total_score": total_score,
        "result": result_label
    })

@app.route('/history', methods=['GET'])
def history():
    return jsonify(get_all_evaluations())

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)