function createThumbnailCard(drawing, file) {
    const col = document.createElement("div");
    col.className = "col";
    col.dataset.filename = drawing.filename;

    col.innerHTML = `
        <div class="card h-100 thumbnail-card">
            <div class="card-img-top thumbnail-img-wrap">
                <img src="" alt="${drawing.filename}"
                     class="thumbnail-img img-fluid" loading="lazy">
            </div>
            <div class="card-body p-2">
                <span class="badge bg-primary mb-1">${drawing.key}</span>
                <p class="card-text small text-truncate mb-0" title="${drawing.filename}">
                    ${drawing.filename}
                </p>
            </div>
        </div>
    `;

    // FileReader로 로컬 이미지 미리보기 (서버 요청 없음)
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            col.querySelector(".thumbnail-img").src = e.target.result;
        };
        reader.readAsDataURL(file);
    }

    return col;
}

function createFailureCard(filename) {
    const col = document.createElement("div");
    col.className = "col";
    col.innerHTML = `
        <div class="card h-100 border-warning thumbnail-card">
            <div class="card-img-top thumbnail-img-wrap bg-light d-flex align-items-center justify-content-center text-muted">
                <span style="font-size: 2rem;">⚠️</span>
            </div>
            <div class="card-body p-2">
                <span class="badge bg-warning text-dark mb-1">파싱 실패</span>
                <p class="card-text small text-truncate mb-0 text-muted" title="${filename}">
                    ${filename}
                </p>
            </div>
        </div>
    `;
    return col;
}

window.renderPreview = function(parseData, imageFiles) {
    const grid = document.getElementById("thumbnail-grid");
    grid.innerHTML = "";

    const fileMap = {};
    imageFiles.forEach(f => fileMap[f.name] = f);

    parseData.drawings.forEach(drawing => {
        const file = fileMap[drawing.filename] || null;
        const card = createThumbnailCard(drawing, file);
        grid.appendChild(card);
    });

    document.getElementById("badge-count").textContent =
        `${parseData.drawings.length}장`;

    // Sortable 초기화
    Sortable.create(grid, {
        animation: 150,
        ghostClass: "sortable-ghost",
        dragClass: "sortable-drag",
    });

    const alertWarnings = document.getElementById("alert-warnings");
    const alertErrors = document.getElementById("alert-errors");
    alertWarnings.classList.add("d-none");
    alertErrors.classList.add("d-none");

    if (parseData.warnings && parseData.warnings.length > 0) {
        alertWarnings.innerHTML = parseData.warnings.map(w => `⚠️ ${w.detail}`).join("<br>");
        alertWarnings.classList.remove("d-none");
    }

    if (parseData.errors && parseData.errors.length > 0) {
        alertErrors.innerHTML = parseData.errors.map(e => `🔴 ${e.detail}`).join("<br>");
        alertErrors.classList.remove("d-none");
    }

    const failuresSection = document.getElementById("section-failures");
    const failuresList = document.getElementById("list-failures");
    if (parseData.failures && parseData.failures.length > 0) {
        failuresList.innerHTML = parseData.failures
            .map(f => `<li>• ${f}</li>`)
            .join("");
        failuresSection.classList.remove("d-none");
    } else {
        failuresSection.classList.add("d-none");
    }
};

function getCurrentOrder() {
    const grid = document.getElementById("thumbnail-grid");
    return Array.from(grid.querySelectorAll("[data-filename]"))
        .map(el => el.dataset.filename);
}

document.getElementById("btn-insert").addEventListener("click", async () => {
    const order = getCurrentOrder();
    const imagesPerPage = parseInt(
        document.querySelector('input[name="images_per_page"]:checked').value
    );
    document.getElementById("section-preview").classList.add("d-none");
    document.getElementById("section-result").classList.remove("d-none");

    window.startInsert(appState.jobId, order, imagesPerPage);
});
