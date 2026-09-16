const fileInput = document.getElementById('videoUpload');
const fileNameLabel = document.getElementById('fileName');
const resultsEl = document.getElementById('results');

fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    fileNameLabel.textContent = file ? file.name : 'Choose a video file';
});

function scoreClass(score, max) {
    const ratio = score / max;
    if (ratio >= 0.7) return 'good';
    if (ratio >= 0.4) return 'mid';
    return 'low';
}

function moduleRow(name, score, max, detailLines) {
    const cls = scoreClass(score, max);
    const pct = Math.max(0, Math.min(100, (score / max) * 100));
    return `
        <div class="module">
            <div class="module__head">
                <span class="module__name">${name}</span>
                <span class="module__score score--${cls}">${score}/${max}</span>
            </div>
            <div class="module__bar-track">
                <div class="module__bar-fill bar--${cls}" style="width:${pct}%"></div>
            </div>
            <p class="module__detail">${detailLines}</p>
        </div>
    `;
}

document.getElementById('evaluateBtn').addEventListener('click', async () => {
    const file = fileInput.files[0];
    if (!file) {
        alert('Please choose a video file first.');
        return;
    }

    const formData = new FormData();
    formData.append('video', file);

    resultsEl.innerHTML = '<p class="results__status">Processing video&hellip;</p>';

    try {
        const response = await fetch('http://127.0.0.1:5000/evaluate', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (data.error) {
            resultsEl.innerHTML = `<p class="error">${data.error}</p>`;
            return;
        }

        const attention = data.driver_attention;
        const lane = data.lane_discipline;
        const safety = data.safety_checks;
        const signal = data.signal_compliance;
        const unsafe = data.unsafe_behavior;

        const totalScore = data.total_score;
        const passFail = data.result;

        resultsEl.innerHTML = `
            ${moduleRow(
                'Driver attention', attention.attention_score, 20,
                `${attention.drowsy_frames} drowsy &middot; ${attention.looked_away_frames} looked away &middot; ${attention.face_detected_frames}/${attention.total_frames} frames with a face detected`
            )}
            ${moduleRow(
                'Lane discipline', lane.lane_discipline_score, 20,
                `${lane.in_lane_frames} in lane &middot; ${lane.out_of_lane_frames} out of lane &middot; ${lane.lane_detected_frames}/${lane.total_frames} frames with lanes detected`
            )}
            ${moduleRow(
                'Safety checks', safety.safety_score, 20,
                `Phone usage in ${safety.phone_detected_frames} of ${safety.analyzed_frames} analyzed frames &middot; seatbelt check: ${safety.seatbelt_check}`
            )}
            ${moduleRow(
                'Signal compliance', signal.signal_compliance_score, 20,
                `${signal.red_light_frames} red-light frames &middot; ${signal.violation_frames} flagged violations of ${signal.analyzed_frames} analyzed`
            )}
            ${moduleRow(
                'Unsafe behavior', unsafe.unsafe_behavior_score, 20,
                `${unsafe.unsafe_event_frames} sudden-motion events of ${unsafe.analyzed_frames} analyzed frames`
            )}

            <div class="total">
                <p class="total__score">${totalScore}<span class="total__max">/100</span></p>
                <span class="verdict verdict--${passFail === 'PASS' ? 'pass' : 'fail'}">${passFail}</span>
            </div>
        `;
    } catch (error) {
        resultsEl.innerHTML = `<p class="error">Error: ${error.message}</p>`;
        console.error(error);
    }
});