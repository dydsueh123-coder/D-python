// 전역 상태 (다른 JS 파일에서도 참조)
window.appState = {
    docxFile: null,
    imageFiles: [],
    jobId: null,
};

function initDropZone(dropzoneEl, inputEl, onFilesSelected) {
    dropzoneEl.addEventListener("click", () => inputEl.click());

    dropzoneEl.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzoneEl.classList.add("drop-zone--active");
    });

    dropzoneEl.addEventListener("dragleave", () => {
        dropzoneEl.classList.remove("drop-zone--active");
    });

    dropzoneEl.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzoneEl.classList.remove("drop-zone--active");
        const files = Array.from(e.dataTransfer.files);
        onFilesSelected(files);
    });

    inputEl.addEventListener("change", () => {
        const files = Array.from(inputEl.files);
        onFilesSelected(files);
    });
}

function showFilename(dropzoneEl, text) {
    const label = dropzoneEl.querySelector(".drop-zone__filename");
    const subText = dropzoneEl.querySelector(".drop-zone__text");
    label.textContent = text;
    label.classList.remove("d-none");
    subText.classList.add("d-none");
}

function checkBothSelected() {
    const both = appState.docxFile && appState.imageFiles.length > 0;
    document.getElementById("btn-parse").disabled = !both;
}

// docx 드롭존
initDropZone(
    document.getElementById("dropzone-docx"),
    document.getElementById("input-docx"),
    (files) => {
        const docx = files.find(f => f.name.endsWith(".docx"));
        if (!docx) {
            alert(".docx 파일을 선택해주세요.");
            return;
        }
        appState.docxFile = docx;
        showFilename(document.getElementById("dropzone-docx"), docx.name);
        checkBothSelected();
    }
);

// 이미지 드롭존
initDropZone(
    document.getElementById("dropzone-images"),
    document.getElementById("input-images"),
    (files) => {
        const allowed = new Set([".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif"]);
        const images = files.filter(f => {
            const ext = f.name.slice(f.name.lastIndexOf(".")).toLowerCase();
            return allowed.has(ext);
        });
        if (images.length === 0) {
            alert("이미지 파일(.png, .jpg 등)을 선택해주세요.");
            return;
        }
        appState.imageFiles = images;
        showFilename(
            document.getElementById("dropzone-images"),
            `${images.length}개 파일 선택됨`
        );
        checkBothSelected();
    }
);

// "파싱 확인" 버튼 클릭 → 파일 업로드 + 파싱 요청
document.getElementById("btn-parse").addEventListener("click", async () => {
    const btn = document.getElementById("btn-parse");
    btn.disabled = true;
    btn.textContent = "업로드 중...";

    try {
        // 1. 파일 업로드
        const formData = new FormData();
        formData.append("docx", appState.docxFile);
        appState.imageFiles.forEach(f => formData.append("images", f));

        const uploadRes = await fetch("/api/upload", { method: "POST", body: formData });
        if (!uploadRes.ok) throw new Error("업로드 실패");
        const uploadData = await uploadRes.json();
        appState.jobId = uploadData.job_id;

        // 2. 파싱 결과 요청
        const parseRes = await fetch("/api/parse", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filenames: uploadData.images }),
        });
        const parseData = await parseRes.json();

        // 3. 프리뷰 화면으로 전환
        window.renderPreview(parseData, appState.imageFiles);
        document.getElementById("section-upload").classList.add("d-none");
        document.getElementById("section-preview").classList.remove("d-none");

    } catch (err) {
        alert("오류가 발생했습니다: " + err.message);
        btn.disabled = false;
        btn.textContent = "파싱 확인 →";
    }
});

// "다시 선택" 버튼
document.getElementById("btn-reset").addEventListener("click", () => {
    appState.docxFile = null;
    appState.imageFiles = [];
    appState.jobId = null;
    document.getElementById("section-preview").classList.add("d-none");
    document.getElementById("section-upload").classList.remove("d-none");
    document.getElementById("btn-parse").disabled = true;
    document.getElementById("btn-parse").textContent = "파싱 확인 →";
});
