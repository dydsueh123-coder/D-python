"""
대용량 삽입 통합 테스트: 100장 이미지 삽입 시 정상 완료 + 메모리 허용 범위 확인.
generate_test_images.py 실행 후 사용 가능.
"""
import pytest
import tracemalloc
from pathlib import Path
from docx import Document
from core.inserter import insert_drawings, InsertConfig

TEST_IMAGES_DIR = Path(__file__).parent / "test_images_100"


@pytest.mark.skipif(
    not TEST_IMAGES_DIR.exists(),
    reason="test_images_100 폴더 없음 — generate_test_images.py 먼저 실행"
)
def test_100장_삽입_완료(tmp_path):
    # 테스트용 빈 docx 생성
    docx_path = tmp_path / "base.docx"
    doc = Document()
    doc.add_paragraph("기존 본문")
    doc.save(docx_path)

    image_paths = sorted(TEST_IMAGES_DIR.glob("*.png"))[:100]
    output_path = tmp_path / "output_100.docx"

    tracemalloc.start()
    config = InsertConfig()
    result = insert_drawings(docx_path, image_paths, output_path, config)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    peak_mb = peak / 1024 / 1024
    print(f"\n삽입 결과: {result['inserted']}장 / 메모리 피크: {peak_mb:.1f} MB")

    assert result["inserted"] == 100
    assert output_path.exists()
    # 메모리 피크 500MB 이하 (A4 PNG 100장 기준 허용치)
    assert peak_mb < 500, f"메모리 과다 사용: {peak_mb:.1f} MB"
