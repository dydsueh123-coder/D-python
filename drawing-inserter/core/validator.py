def check_continuity(drawings: list[dict]) -> list[int]:
    """
    정수 번호 기준으로 빠진 번호를 반환한다.
    서브번호(3a, 3b)가 있는 경우 해당 정수 번호는 갭으로 처리하지 않는다.
    """
    if not drawings:
        return []

    nums = set(d["num"] for d in drawings)
    min_n, max_n = min(nums), max(nums)
    gaps = [n for n in range(min_n, max_n + 1) if n not in nums]
    return gaps


def check_duplicates(drawings: list[dict]) -> list[str]:
    """동일 key가 2번 이상 나타나는 경우 해당 key 목록 반환"""
    from collections import Counter
    counts = Counter(d["key"] for d in drawings)
    return [key for key, cnt in counts.items() if cnt > 1]


def build_report(drawings: list[dict], failures: list[str]) -> dict:
    """
    삽입 전 검증 리포트 생성.
    status: PASS / WARNING / FAIL
    """
    gaps = check_continuity(drawings)
    dups = check_duplicates(drawings)

    errors = []
    warnings = []

    if dups:
        errors.append({"type": "DUPLICATE", "detail": f"중복 도면번호: {', '.join(dups)}"})
    if failures:
        warnings.append({"type": "PARSE_FAIL", "detail": f"파싱 실패 파일 {len(failures)}건: {', '.join(failures)}"})
    if gaps:
        warnings.append({"type": "GAP", "detail": f"번호 불연속: {gaps}"})

    # 유효 도면이 하나도 없으면 삽입 불가 → FAIL
    if not drawings and failures:
        errors.append({"type": "NO_VALID_DRAWINGS", "detail": "삽입 가능한 도면이 없습니다 (모든 파일 파싱 실패)"})

    if errors:
        status = "FAIL"
    elif warnings:
        status = "WARNING"
    else:
        status = "PASS"

    return {
        "status": status,
        "total": len(drawings),
        "errors": errors,
        "warnings": warnings,
        "drawings": drawings,
        "failures": failures,
    }
