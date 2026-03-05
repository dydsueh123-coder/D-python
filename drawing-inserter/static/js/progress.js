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
            const report = msg.report;

            // 요약 배너
            const failNote = r.failures && r.failures.length > 0
                ? ` / 제외 ${r.failures.length}건` : "";
            document.getElementById("result-summary").innerHTML =
                `삽입 완료 &mdash; 총 입력 <strong>${r.total_input}장</strong> &nbsp;|&nbsp; `
                + `성공 <strong>${r.inserted}장</strong>${failNote}`;

            // 삽입 성공 테이블
            const successBody = document.getElementById("report-success-body");
            successBody.innerHTML = "";
            (r.drawings || []).forEach((d, idx) => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td class="text-center text-muted">${idx + 1}</td>
                    <td class="fw-medium">【도 ${d.key}】</td>
                    <td class="text-truncate" style="max-width:300px" title="${d.filename}">${d.filename}</td>
                    <td class="text-center"><span class="badge bg-success">삽입됨</span></td>
                `;
                successBody.appendChild(tr);
            });

            // 파싱 실패 테이블
            if (r.failures && r.failures.length > 0) {
                const failBody = document.getElementById("report-failures-body");
                failBody.innerHTML = "";
                r.failures.forEach((fname, idx) => {
                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td class="text-center text-muted">${idx + 1}</td>
                        <td class="text-truncate" style="max-width:360px" title="${fname}">${fname}</td>
                        <td class="text-warning fw-medium">도면번호 인식 실패</td>
                    `;
                    failBody.appendChild(tr);
                });
                document.getElementById("report-failures-wrap").classList.remove("d-none");
            }

            // 갭/중복 경고
            if (report && (report.warnings.length > 0 || report.errors.length > 0)) {
                const items = [...(report.errors || []), ...(report.warnings || [])];
                document.getElementById("report-warnings-content").innerHTML =
                    items.map(w => `⚠️ ${w.detail}`).join("<br>");
                document.getElementById("report-warnings-wrap").classList.remove("d-none");
            }

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
