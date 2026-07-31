# floorplan-ai

PNG/JPG/PDF 평면도를 분석해 OCR 결과, 벽·문·창·방 영역과 항목별 신뢰도를 `floorplan.json` 및 SVG로 저장하는 테스트 가능한 CLI입니다.

## 설치와 실행

```bash
pip install -e ".[vision,ocr,pdf,dev]"
floorplan analyze plan.pdf --output-dir out --lang kor+eng
```

Tesseract 또는 OpenCV가 없는 경우에도 입력 검증, JSON 스키마, SVG 생성과 CLI 테스트는 동작합니다. 이 경우 해당 검출기는 빈 결과와 낮은 신뢰도를 반환합니다.

```text
out/floorplan.json
out/floorplan.svg
```

좌표 원점은 이미지 좌상단이며 픽셀 단위입니다. `confidence`는 0~1 사이의 휴리스틱 값이며, 정밀한 도면 변환 전 사람이 확인해야 합니다. SketchUp 연동은 포함하지 않습니다.
