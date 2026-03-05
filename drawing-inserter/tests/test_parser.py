import pytest
from core.parser import parse_drawing_number, sort_drawings


def test_기본_숫자_파싱():
    assert parse_drawing_number("abcd(1).png") == ("1", 1, "")


def test_서브번호_파싱():
    assert parse_drawing_number("mnop(3a).png") == ("3a", 3, "a")


def test_두자리_숫자():
    assert parse_drawing_number("xyz(10).jpg") == ("10", 10, "")


def test_파싱_실패():
    assert parse_drawing_number("readme.txt") is None


def test_정렬_순서():
    files = ["xyz(10).jpg", "abcd(1).png", "mnop(3a).png", "ijkl(3).png"]
    result = sort_drawings(files)
    keys = [r["key"] for r in result]
    assert keys == ["1", "3", "3a", "10"]


def test_파싱_실패_파일_분리():
    files = ["abcd(1).png", "readme.txt", "xyz(10).jpg"]
    result = sort_drawings(files)
    assert len(result) == 2
    assert all(r["key"] is not None for r in result)
