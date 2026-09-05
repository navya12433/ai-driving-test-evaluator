document.getElementById('evaluateBtn').addEventListener('click', async () => {
    const file = document.getElementById('videoUpload').files[0];
    if (!file) {
        alert('Please upload a video first.');
        return;
    }

    const formData = new FormData();
    formData.append('video', file);

    document.getElementById('results').innerText = 'Processing...';

    try {
        const response = await fetch('http://127.0.0.1:5000/evaluate', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        const attention = data.driver_attention;
        const lane = data.lane_discipline;
        const safety = data.safety_checks;
        const signal = data.signal_compliance;
        const unsafe = data.unsafe_behavior;

        const totalScore = attention.attention_score
            + lane.lane_discipline_score
            + safety.safety_score
            + signal.signal_compliance_score
            + unsafe.unsafe_behavior_score;

        const passFail = totalScore >= 50 ? "PASS" : "FAIL";

        document.getElementById('results').innerHTML = `
            <h2>Driver Attention Report</h2>
            <p>Total Frames: ${attention.total_frames}</p>
            <p>Face Detected: ${attention.face_detected_frames}</p>
            <p>Drowsy Frames: ${attention.drowsy_frames}</p>
            <p>Looked Away Frames: ${attention.looked_away_frames}</p>
            <p><strong>Attention Score: ${attention.attention_score}/20</strong></p>

            <h2>Lane Discipline Report</h2>
            <p>Total Frames: ${lane.total_frames}</p>
            <p>Lanes Detected: ${lane.lane_detected_frames}</p>
            <p>In Lane: ${lane.in_lane_frames}</p>
            <p>Out of Lane: ${lane.out_of_lane_frames}</p>
            <p><strong>Lane Discipline Score: ${lane.lane_discipline_score}/20</strong></p>

            <h2>Safety Checks Report</h2>
            <p>Analyzed Frames: ${safety.analyzed_frames}</p>
            <p>Phone Usage Detected In: ${safety.phone_detected_frames} frames</p>
            <p>Seatbelt Check: ${safety.seatbelt_check}</p>
            <p><strong>Safety Score: ${safety.safety_score}/20</strong></p>

            <h2>Signal Compliance Report</h2>
            <p>Analyzed Frames: ${signal.analyzed_frames}</p>
            <p>Red Light Frames: ${signal.red_light_frames}</p>
            <p>Violation Frames: ${signal.violation_frames}</p>
            <p><strong>Signal Compliance Score: ${signal.signal_compliance_score}/20</strong></p>

            <h2>Unsafe Behavior Report</h2>
            <p>Analyzed Frames: ${unsafe.analyzed_frames}</p>
            <p>Unsafe Event Frames: ${unsafe.unsafe_event_frames}</p>
            <p><strong>Unsafe Behavior Score: ${unsafe.unsafe_behavior_score}/20</strong></p>

            <hr>
            <h2>Total Score: ${totalScore}/100</h2>
            <h2>Result: ${passFail}</h2>
        `;
    } catch (error) {
        document.getElementById('results').innerText = 'Error: ' + error.message;
        console.error(error);
    }
});