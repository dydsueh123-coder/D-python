from dataclasses import dataclass
from pathlib import Path
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from PIL import Image
from core.parser import sort_drawings_with_failures
import shutil


@dataclass
class InsertConfig:
    max_width_cm: float = 14.5
    max_height_cm: float = 22.0       # 1페이지 1장 기준 최대 높이
    max_height_2up_cm: float = 10.0   # 1페이지 2장 기준 장당 최대 높이
    caption_font: str = "맑은 고딕"
    caption_size_pt: int = 12
    caption_template: str = "【도 {key}】"
    images_per_page: int = 1          # 1 또는 2


def _get_image_dimensions(img_path: Path, config: InsertConfig) -> tuple[float, float]:
    """원본 비율 유지하면서 최대 크기 안에 맞는 width, height (cm) 계산"""
    with Image.open(img_path) as img:
        orig_w, orig_h = img.size  # pixels

    # pixels → cm 변환 (96 dpi 기준, 1인치=2.54cm)
    dpi = 96
    w_cm = orig_w / dpi * 2.54
    h_cm = orig_h / dpi * 2.54

    if w_cm > config.max_width_cm:
        ratio = config.max_width_cm / w_cm
        w_cm *= ratio
        h_cm *= ratio

    if h_cm > config.max_height_cm:
        ratio = config.max_height_cm / h_cm
        w_cm *= ratio
        h_cm *= ratio

    return w_cm, h_cm


def _add_page_break(doc):
    """문서에 페이지 나누기 단락 추가"""
    para = doc.add_paragraph()
    run = para.add_run()
    br = OxmlElement("w:br")
    br.set(qn("w:type"), "page")
    run._r.append(br)


def _add_caption(doc, text: str, config: InsertConfig):
    """캡션 단락 추가 (왼쪽 정렬)"""
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = para.add_run(text)
    run.font.name = config.caption_font
    run.font.size = Pt(config.caption_size_pt)


def _add_image(doc, img_path: Path, config: InsertConfig, max_height_cm: float):
    """이미지 단락 추가 (왼쪽 정렬, 지정 높이 기준 축소)"""
    with Image.open(img_path) as img:
        orig_w, orig_h = img.size
    dpi = 96
    w_cm = orig_w / dpi * 2.54
    h_cm = orig_h / dpi * 2.54

    if w_cm > config.max_width_cm:
        ratio = config.max_width_cm / w_cm
        w_cm, h_cm = w_cm * ratio, h_cm * ratio
    if h_cm > max_height_cm:
        ratio = max_height_cm / h_cm
        w_cm, h_cm = w_cm * ratio, h_cm * ratio

    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    para.add_run().add_picture(str(img_path), width=Cm(w_cm))


def _insert_1up(doc, img_path: Path, caption_text: str, config: InsertConfig):
    """1페이지 1장 모드: 페이지 나누기 → 캡션 → 이미지"""
    _add_page_break(doc)
    _add_caption(doc, caption_text, config)
    _add_image(doc, img_path, config, config.max_height_cm)


def _insert_2up(doc, img_path: Path, caption_text: str, config: InsertConfig,
                idx: int, sorted_drawings: list, path_map: dict):
    """
    1페이지 2장 모드.
    짝수 인덱스(0, 2, 4...): 페이지 나누기 후 첫 번째 도면 삽입
    홀수 인덱스(1, 3, 5...): 페이지 나누기 없이 두 번째 도면 이어서 삽입
    """
    if idx % 2 == 0:
        _add_page_break(doc)
    _add_caption(doc, caption_text, config)
    _add_image(doc, img_path, config, config.max_height_2up_cm)


def insert_drawings(
    docx_path: Path,
    image_paths: list[Path],
    output_path: Path,
    config: InsertConfig,
    progress_callback=None,  # progress_callback(current, total) 형식
) -> dict:
    """
    원본 docx를 복사해서 이미지를 문서 끝에 삽입한다.
    원본 파일은 절대 수정하지 않는다.
    """
    # 원본 복사 (원본 보존)
    shutil.copy2(docx_path, output_path)
    doc = Document(output_path)

    filenames = [p.name for p in image_paths]
    path_map = {p.name: p for p in image_paths}

    sorted_drawings, failures = sort_drawings_with_failures(filenames)
    total = len(sorted_drawings)
    inserted = 0

    for i, drawing in enumerate(sorted_drawings):
        img_path = path_map[drawing["filename"]]
        key = drawing["key"]
        caption_text = config.caption_template.format(key=key)

        if config.images_per_page == 2:
            _insert_2up(doc, img_path, caption_text, config, i, sorted_drawings, path_map)
        else:
            _insert_1up(doc, img_path, caption_text, config)

        inserted += 1
        if progress_callback:
            progress_callback(i + 1, total)

    doc.save(output_path)

    return {
        "inserted": inserted,
        "failures": failures,
        "total_input": len(image_paths),
        "drawings": sorted_drawings,  # 삽입된 도면 상세 목록 (key, filename)
    }
