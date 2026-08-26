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

        document.getElementById('results').innerHTML = `
            <h2>Driver Attention Report</h2>
            <p>Total Frames: ${data.total_frames}</p>
            <p>Face Detected: ${data.face_detected_frames}</p>
            <p>Drowsy Frames: ${data.drowsy_frames}</p>
            <p>Looked Away Frames: ${data.looked_away_frames}</p>
            <p><strong>Attention Score: ${data.attention_score}/20</strong></p>
        `;
    } catch (error) {
        document.getElementById('results').innerText = 'Error: ' + error.message;
        console.error(error);
    }
});