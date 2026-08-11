#!/bin/bash
# 개인정보 마스킹 (macOS) — 더블클릭으로 실행
cd "$(dirname "$0")"
clear
echo "──────────────────────────────────────────"
echo "  엑셀 개인정보 마스킹"
echo "──────────────────────────────────────────"
echo
echo "  AI에 넣기 전에 개인정보를 자동으로 가립니다."
echo "  · 이름·전화·이메일  →  번호로 치환"
echo "  · 주민번호·계좌·카드  →  컬럼 삭제"
echo "  · 생년월일 → 연령대 / 주소 → 시·구까지"
echo
echo "  ※ 알려진 개인정보 패턴이 남으면 파일을 만들지 않고 멈춥니다."
echo
echo "──────────────────────────────────────────"
echo
echo "  엑셀 파일을 이 창에 끌어다 놓고 엔터를 누르세요."
echo
read -r -p "  파일: " FILEPATH

FILEPATH="${FILEPATH%\"}"; FILEPATH="${FILEPATH#\"}"
FILEPATH="${FILEPATH%\'}"; FILEPATH="${FILEPATH#\'}"
FILEPATH="$(echo "$FILEPATH" | sed 's/\\ / /g' | xargs)"

if [ ! -f "$FILEPATH" ]; then
  echo; echo "  ❌ 파일을 찾을 수 없습니다: $FILEPATH"; echo
  read -r -p "  엔터를 누르면 닫힙니다."; exit 1
fi

python3 -c "import openpyxl" 2>/dev/null || {
  echo; echo "  처음 실행이라 필요한 도구를 설치합니다 (1회, 약 10초)..."
  pip3 install --quiet openpyxl 2>/dev/null || pip3 install --quiet --break-system-packages openpyxl
}

echo
OUTPUT="$(python3 "$(dirname "$0")/../mask_excel.py" "$FILEPATH" 2>&1)"
STATUS=$?
printf '%s\n' "$OUTPUT"
echo
if [ $STATUS -eq 0 ]; then
  MASKED_PATH="$(printf '%s\n' "$OUTPUT" | sed -n 's/^마스킹: //p' | tail -1)"
  echo "  새로 만든 마스킹 파일을 선택해서 보여드립니다."
  if [ -n "$MASKED_PATH" ] && [ -f "$MASKED_PATH" ]; then
    open -R "$MASKED_PATH"
  else
    open "$(dirname "$FILEPATH")"
  fi
else
  echo "  ⚠️ 개인정보가 남아 있어 파일을 만들지 않았습니다. 위 내용을 확인하세요."
fi
echo
read -r -p "  엔터를 누르면 닫힙니다."
