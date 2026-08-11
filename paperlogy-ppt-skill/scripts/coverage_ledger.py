#!/usr/bin/env python3
# coverage_ledger.py <파일.pptx>
# "모든 글/전부/다 읽히게/싹" 같이 '전체'를 지시받았을 때,
# 텍스트 블록을 하나도 빠짐없이 자동 나열한다. 제작자는 각 블록에
# [손봄 / 유지(이유)]를 채워 장부로 낸다 — '일부만 하고 나머진 멀쩡'으로
# 몰래 좁히는 걸 구조로 막는다.
import sys
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

def walk(shapes):
    for s in shapes:
        if s.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from walk(s.shapes)
        elif s.has_text_frame:
            yield s

def main(path):
    prs = Presentation(path)
    n = 0
    print("=" * 64)
    print("커버리지 장부 — 각 블록에 [손봄] 또는 [유지: 이유] 를 채울 것")
    print("'멀쩡'도 이유와 함께 장부에 남겨야 인정. 빈 칸 = 미점검 = 미완성")
    print("=" * 64)
    for si, sl in enumerate(prs.slides, 1):
        for sh in walk(sl.shapes):
            t = sh.text_frame.text.strip()
            if not t:
                continue
            # 라벨·숫자·코드값 등 1줄 짧은 메타는 별도 표시(그래도 나열은 함)
            short = len(t) <= 14 and "\n" not in t
            n += 1
            head = t.replace("\n", " / ")
            if len(head) > 90:
                head = head[:90] + "…"
            tag = " (짧은 라벨/메타)" if short else ""
            print(f"[{n:3}] s{si}{tag}: {head}")
            print(f"      상태: ____________________")
    print("=" * 64)
    print(f"총 텍스트 블록 {n}개 — 전부 '상태'가 채워졌는지 확인하고 보고에 동반.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용: python3 coverage_ledger.py <파일.pptx>")
        sys.exit(1)
    main(sys.argv[1])
