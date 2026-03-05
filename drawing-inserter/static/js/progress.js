window.startInsert = async function(jobId, order) {
    const progressLabel = document.getElementById("progress-label");
    const progressBar = document.getElementById("progress-bar");
    const resultProgress = document.getElementById("result-progress");
    const resultDone = document.getElementById("result-done");
    const resultError = document.getElementById("result-error");

    progressLabel.textContent = "삽입 시작 중...";
    progressBar.style.width = "0%";
    progressBar.textContent = "0%";
    resultProgress.classList.remove("d-none");
    resultDone.classList.add("d-none");
    resultError.classList.add("d-none");

    // 1. 삽입 작업 시작 요청
    const res = await fetch(`/api/insert/${jobId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ order }),
    });

    if (!res.ok) {
        showError("삽입 요청 실패. 다시 시도해주세요.");
        return;
    }

    // 2. SSE로 진행률 수신
    const sse = new EventSource(`/api/progress/${jobId}`);

    sse.onmessage = (event) => {
        const msg = JSON.parse(event.data);

        if (msg.type === "progress") {
            const pct = Math.round((msg.current / msg.total) * 100);
            progressBar.style.width = `${pct}%`;
            progressBar.textContent = `${pct}%`;
            progressLabel.textContent = `${msg.current} / ${msg.total} 장 삽입 중...`;
        }

        if (msg.type === "done") {
            sse.close();
            progressBar.style.width = "100%";
            progressBar.textContent = "100%";

            const r = msg.result;
            const failNote = r.failures && r.failures.length > 0
                ? `<br><small>파싱 실패로 제외된 파일: ${r.failures.length}건</small>`
                : "";
            document.getElementById("result-summary").innerHTML =
                `✅ 삽입 완료 — ${r.inserted}장 정상 삽입 (입력: ${r.total_input}장)${failNote}`;

            resultProgress.classList.add("d-none");
            resultDone.classList.remove("d-none");

            document.getElementById("btn-download").onclick = () => {
                window.location.href = `/api/download/${jobId}`;
            };
        }

        if (msg.type === "error") {
            sse.close();
            showError(msg.message || "알 수 없는 오류가 발생했습니다.");
        }
    };

    sse.onerror = () => {
        sse.close();
        showError("서버 연결이 끊어졌습니다. 페이지를 새로고침하고 다시 시도해주세요.");
    };

    function showError(message) {
        resultProgress.classList.add("d-none");
        resultError.classList.remove("d-none");
        document.getElementById("result-error-message").textContent = message;
    }
};

document.getElementById("btn-new").addEventListener("click", () => {
    window.location.reload();
});

document.getElementById("btn-retry").addEventListener("click", () => {
    window.location.reload();
});
