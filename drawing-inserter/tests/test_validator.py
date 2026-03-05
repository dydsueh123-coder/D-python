from core.validator import check_continuity, check_duplicates, build_report


def test_연속_번호_정상():
    drawings = [
        {"key": "1", "num": 1, "alpha": ""},
        {"key": "2", "num": 2, "alpha": ""},
        {"key": "3", "num": 3, "alpha": ""},
    ]
    gaps = check_continuity(drawings)
    assert gaps == []


def test_번호_갭_감지():
    drawings = [
        {"key": "1", "num": 1, "alpha": ""},
        {"key": "3", "num": 3, "alpha": ""},  # 2 빠짐
    ]
    gaps = check_continuity(drawings)
    assert 2 in gaps


def test_서브번호_있으면_갭_아님():
    # 3, 3a, 4 → 갭 없음
    drawings = [
        {"key": "3", "num": 3, "alpha": ""},
        {"key": "3a", "num": 3, "alpha": "a"},
        {"key": "4", "num": 4, "alpha": ""},
    ]
    assert check_continuity(drawings) == []


def test_중복_감지():
    drawings = [
        {"key": "1", "num": 1, "alpha": ""},
        {"key": "1", "num": 1, "alpha": ""},  # 중복
    ]
    dups = check_duplicates(drawings)
    assert "1" in dups


def test_리포트_PASS():
    drawings = [
        {"key": "1", "num": 1, "alpha": "", "filename": "a(1).png"},
        {"key": "2", "num": 2, "alpha": "", "filename": "b(2).png"},
    ]
    report = build_report(drawings, failures=[])
    assert report["status"] == "PASS"
    assert report["total"] == 2


def test_리포트_FAIL_누락():
    report = build_report([], failures=["a(1).png", "b(2).png"])
    assert report["status"] == "FAIL"
