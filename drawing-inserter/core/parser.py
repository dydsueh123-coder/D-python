import re
from pathlib import Path

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif"}

# 기본 패턴: 파일명(번호).확장자
# 번호는 숫자 + 선택적 알파벳 (예: 1, 3a, 10b)
_PATTERN = re.compile(r'\(([0-9]+[a-zA-Z]?)\)')


def parse_drawing_number(filename: str):
    """
    파일명에서 도면 번호를 추출한다.
    성공: ("3a", 3, "a") 형식의 튜플 반환
    실패: None 반환
    """
    path = Path(filename)
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return None

    match = _PATTERN.search(path.name)
    if not match:
        return None

    raw = match.group(1)  # "3a"
    num_part = int(re.match(r'\d+', raw).group())
    alpha_part = re.sub(r'^\d+', '', raw)  # "" or "a"
    return (raw, num_part, alpha_part)


def sort_drawings(filenames: list[str]) -> list[dict]:
    """
    파일명 목록을 파싱해서 정렬된 결과 반환.
    각 항목: {"filename": str, "key": str, "num": int, "alpha": str}
    파싱 실패 파일은 결과에서 제외
    """
    results = []
    for fname in filenames:
        parsed = parse_drawing_number(fname)
        if parsed:
            key, num, alpha = parsed
            results.append({"filename": fname, "key": key, "num": num, "alpha": alpha})

    results.sort(key=lambda x: (x["num"], x["alpha"]))
    return results


def sort_drawings_with_failures(filenames: list[str]) -> tuple[list[dict], list[str]]:
    """정렬 성공 목록, 파싱 실패 파일명 목록을 함께 반환"""
    success = []
    failures = []
    for fname in filenames:
        parsed = parse_drawing_number(fname)
        if parsed:
            key, num, alpha = parsed
            success.append({"filename": fname, "key": key, "num": num, "alpha": alpha})
        else:
            failures.append(fname)
    success.sort(key=lambda x: (x["num"], x["alpha"]))
    return success, failures
