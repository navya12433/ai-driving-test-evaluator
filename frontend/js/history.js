const listEl = document.getElementById('historyList');

function verdictClass(result) {
    return result === 'PASS' ? 'pass' : 'fail';
}

function formatDate(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString();
}

function historyRow(entry) {
    return `
        <div class="module">
            <div class="module__head">
                <span class="module__name">${entry.filename}</span>
                <span class="module__score score--${entry.result === 'PASS' ? 'good' : 'low'}">${entry.total_score}/100</span>
            </div>
            <p class="module__detail">
                Attention ${entry.attention_score}/20 &middot;
                Lane ${entry.lane_discipline_score}/20 &middot;
                Safety ${entry.safety_score}/20 &middot;
                Signal ${entry.signal_compliance_score}/20 &middot;
                Unsafe ${entry.unsafe_behavior_score}/20
            </p>
            <p class="module__detail">
                ${formatDate(entry.created_at)} &middot;
                <span class="verdict verdict--${verdictClass(entry.result)}" style="padding:2px 10px;font-size:12px;margin-top:0;display:inline-block;">${entry.result}</span>
            </p>
        </div>
    `;
}

async function loadHistory() {
    try {
        const response = await fetch('http://127.0.0.1:5000/history');
        const data = await response.json();

        if (!data.length) {
            listEl.innerHTML = '<p class="results__status">No evaluations yet. Run one from the evaluation page.</p>';
            return;
        }

        listEl.innerHTML = data.map(historyRow).join('');
    } catch (error) {
        listEl.innerHTML = `<p class="error">Error loading history: ${error.message}</p>`;
        console.error(error);
    }
}

loadHistory();