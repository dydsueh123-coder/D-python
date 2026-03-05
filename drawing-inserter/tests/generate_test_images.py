"""
100장 테스트 이미지 생성 스크립트.
대용량 삽입 성능/메모리 테스트용. 실제 배포에는 포함하지 않는다.
"""
from PIL import Image
from pathlib import Path

out_dir = Path(__file__).parent / "test_images_100"
out_dir.mkdir(exist_ok=True)

for i in range(1, 101):
    # A4 300dpi 크기 (2480x3508) — 실제 도면 크기 시뮬레이션
    img = Image.new("RGB", (2480, 3508), color=(255, 255, 255))
    img.save(out_dir / f"drawing({i}).png")
    print(f"생성: drawing({i}).png")

print(f"\n완료: {out_dir} 에 100장 생성됨")
