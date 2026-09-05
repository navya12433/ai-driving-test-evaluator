
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

app = Flask(__name__)
CORS(app)

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

    return jsonify({
        "driver_attention": attention_result,
        "lane_discipline": lane_result,
        "safety_checks": safety_result,
        "signal_compliance": signal_result
    })

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)