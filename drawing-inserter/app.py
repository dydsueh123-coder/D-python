import uuid
import json
import queue
import threading
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_file, Response
from config import Config
from core.parser import sort_drawings_with_failures
from core.validator import build_report
from core.inserter import insert_drawings, InsertConfig
from docx.opc.exceptions import PackageNotFoundError
from docx import Document

app = Flask(__name__)
app.config.from_object(Config)
Config.ensure_dirs()

# SSE 진행률 큐: {job_id: Queue}
_progress_queues: dict[str, queue.Queue] = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/parse", methods=["POST"])
def api_parse():
    """이미지 파일명 목록을 파싱해서 정렬 결과 + 검증 리포트 반환"""
    filenames = request.json.get("filenames", [])
    if not filenames:
        return jsonify({"error": "filenames 필드가 필요합니다"}), 400

    sorted_drawings, failures = sort_drawings_with_failures(filenames)
    report = build_report(sorted_drawings, failures)
    return jsonify(report)


@app.route("/api/upload", methods=["POST"])
def api_upload():
    """docx + 이미지 파일을 업로드하고 job_id를 반환"""
    if "docx" not in request.files:
        return jsonify({"error": "docx 파일이 없습니다"}), 400
    if "images" not in request.files:
        return jsonify({"error": "이미지 파일이 없습니다"}), 400

    job_id = str(uuid.uuid4())
    job_dir = Config.UPLOAD_FOLDER / job_id
    job_dir.mkdir()

    docx_file = request.files["docx"]
    docx_path = job_dir / "input.docx"
    docx_file.save(docx_path)

    # 유효한 docx인지 사전 확인
    try:
        Document(docx_path)
    except PackageNotFoundError:
        docx_path.unlink(missing_ok=True)
        job_dir.rmdir()
        return jsonify({"error": "유효하지 않은 docx 파일입니다"}), 400

    image_paths = []
    for img_file in request.files.getlist("images"):
        suffix = Path(img_file.filename).suffix.lower()
        if suffix not in Config.ALLOWED_IMAGES:
            continue
        img_path = job_dir / img_file.filename
        img_file.save(img_path)
        image_paths.append(img_file.filename)

    return jsonify({"job_id": job_id, "image_count": len(image_paths), "images": image_paths})


@app.route("/api/insert/<job_id>", methods=["POST"])
def api_insert(job_id):
    """삽입 작업을 백그라운드로 실행하고 즉시 응답. 진행률은 SSE로 확인."""
    body = request.json or {}
    ordered_filenames = body.get("order")

    job_dir = Config.UPLOAD_FOLDER / job_id
    if not job_dir.exists():
        return jsonify({"error": "job_id가 유효하지 않습니다"}), 404

    docx_path = job_dir / "input.docx"
    output_path = Config.OUTPUT_FOLDER / f"{job_id}_result.docx"

    if ordered_filenames:
        image_paths = [job_dir / fn for fn in ordered_filenames]
    else:
        image_paths = sorted(
            [p for p in job_dir.iterdir() if p.suffix.lower() in Config.ALLOWED_IMAGES]
        )

    q = queue.Queue()
    _progress_queues[job_id] = q

    def run_insert():
        try:
            def on_progress(current, total):
                q.put({"type": "progress", "current": current, "total": total})

            config = InsertConfig()
            result = insert_drawings(docx_path, image_paths, output_path, config, on_progress)
            q.put({"type": "done", "result": result})
        except Exception as e:
            q.put({"type": "error", "message": str(e)})
        finally:
            _progress_queues.pop(job_id, None)

    threading.Thread(target=run_insert, daemon=True).start()
    return jsonify({"status": "started"})


@app.route("/api/progress/<job_id>")
def api_progress(job_id):
    """SSE 엔드포인트. 삽입 진행률을 실시간으로 전달."""
    def event_stream():
        q = _progress_queues.get(job_id)
        if not q:
            yield f"data: {json.dumps({'type': 'error', 'message': 'job not found'})}\n\n"
            return

        while True:
            try:
                msg = q.get(timeout=30)
                yield f"data: {json.dumps(msg)}\n\n"
                if msg["type"] in ("done", "error"):
                    break
            except queue.Empty:
                yield "data: {\"type\": \"ping\"}\n\n"

    return Response(event_stream(), mimetype="text/event-stream")


@app.route("/api/download/<job_id>")
def api_download(job_id):
    output_path = Config.OUTPUT_FOLDER / f"{job_id}_result.docx"
    if not output_path.exists():
        return jsonify({"error": "결과 파일이 없습니다"}), 404
    return send_file(output_path, as_attachment=True, download_name="result.docx")


@app.errorhandler(413)
def request_entity_too_large(e):
    return jsonify({"error": "파일 크기가 너무 큽니다 (docx 최대 20MB, 이미지 총합 최대 200MB)"}), 413


if __name__ == "__main__":
    app.run(debug=True, port=5100)
