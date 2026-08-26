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
        `;
    } catch (error) {
        document.getElementById('results').innerText = 'Error: ' + error.message;
        console.error(error);
    }
});