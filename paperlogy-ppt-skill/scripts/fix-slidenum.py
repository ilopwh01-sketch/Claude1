#!/usr/bin/env python3
# 자동 슬라이드 번호(slidenum fld)의 rPr에 서식을 직접 주입 —
# PowerPoint가 마스터 기본 서식으로 덮지 못하게. 기존 텍스트 번호와 100% 동일 디자인.
# 사용: python3 fix-slidenum.py <pptx> [폰트] [hex색] [pt크기]
import zipfile, re, os, shutil, sys
PPTX = sys.argv[1]
FONT = sys.argv[2] if len(sys.argv) > 2 else "Pretendard"
HEX  = sys.argv[3] if len(sys.argv) > 3 else "8E8E93"
SZ   = str(int(float(sys.argv[4] if len(sys.argv) > 4 else 8) * 100))  # pt → OOXML(1/100)

RPR = (f'<a:rPr b="0" lang="en-US" sz="{SZ}">'
       f'<a:solidFill><a:srgbClr val="{HEX}"/></a:solidFill>'
       f'<a:latin typeface="{FONT}"/><a:ea typeface="{FONT}"/><a:cs typeface="{FONT}"/>'
       f'</a:rPr>')

with zipfile.ZipFile(PPTX) as z:
    names = z.namelist()
    data = {n: z.read(n) for n in names}

def dedupe_cnvpr_ids(x):
    # pptxgenjs가 s.slideNumber placeholder id를 25로 하드코딩 → 도형 25개 넘는 밀도
    # 슬라이드에서 자동번호 도형과 충돌하면 PowerPoint가 "복구" 창을 띄운다.
    # 슬라이드 안에서 중복된 <p:cNvPr id="N">를 max+1, max+2…로 유니크하게 재배정.
    ids = [int(i) for i in re.findall(r'<p:cNvPr id="(\d+)"', x)]
    if not ids:
        return x, 0
    seen, mx, fixed = set(), [max(ids)], [0]
    def rep(m):
        i = m.group(1)
        if i in seen:
            mx[0] += 1; fixed[0] += 1
            return m.group(0).replace(f'id="{i}"', f'id="{mx[0]}"', 1)
        seen.add(i)
        return m.group(0)
    x = re.sub(r'<p:cNvPr id="(\d+)"', rep, x)
    return x, fixed[0]

id_fixed = 0
patched = 0
for n in list(data):
    if re.match(r'ppt/slides/slide\d+\.xml$', n):
        x = data[n].decode("utf-8")
        x, _nf = dedupe_cnvpr_ids(x)
        id_fixed += _nf
        data[n] = x.encode("utf-8")
        def repl(m):
            global patched
            blk = m.group(0)
            blk2 = re.sub(r'<a:rPr\b[^>]*/>', RPR, blk, count=1)  # fld 안 빈 rPr → 서식 rPr
            if blk2 != blk: patched += 1
            return blk2
        x = re.sub(r'<a:fld[^>]*type="slidenum">.*?</a:fld>', repl, x, flags=re.S)
        data[n] = x.encode("utf-8")

tmp = PPTX + ".tmp"
with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
    for n in names:
        z.writestr(n, data[n])
shutil.move(tmp, PPTX)
print(f"slidenum rPr 서식 주입 완료: {patched}개 슬라이드 ({FONT} {int(int(SZ)/100)}pt #{HEX})")
if id_fixed:
    print(f"cNvPr 중복 id 재배정: {id_fixed}건 (PowerPoint 복구창 유발 충돌 제거)")
