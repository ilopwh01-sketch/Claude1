#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# build_ppt.py — PPT 강제 빌드 래퍼 (PPT 제작 전용, 예외 없음)
# 🔒 PPT는 'node build.js' 직접 실행 대신 반드시 이 래퍼로 빌드한다.
#    1) node로 빌드 → pptx 생성   2) ppt_lint 무조건 실행
#    3) ppt_lint ERROR면 여기서 막힘 (PNG/open 단계로 못 넘어감 = "미완성")
#    4) ERROR 0이면 PNG QA 자동 생성 → 눈 확인 후 open
# 빌드 JS가 ppt_lint 호출을 깜빡해도 이 래퍼가 강제로 검사하므로 누락 불가.
#
# 사용: python3 scripts/build_ppt.py <build.js>
import sys, subprocess, re, os, unicodedata, glob, shutil, uuid, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
# /tmp는 Windows엔 없다(C:\tmp가 없으면 [1/5]에서 바로 죽는다) — OS별 임시 폴더로 통일.
# python3도 Windows엔 보통 없다(그냥 "python") — README가 문서화한 PYTHON 환경변수를 실제로 반영한다.
TMP = tempfile.gettempdir()
PY = os.environ.get("PYTHON", "python3" if shutil.which("python3") else "python")
# --fast = 반복 수정 중 [5/5] 실제 PowerPoint 실렌더 스킵(매 빌드 PowerPoint 뜨는 번거로움 회피).
#   디폴트는 실렌더 ON — 최종 빌드에서 깜빡 빼먹지 않게(빼먹으면 그게 '두 번 지적'의 자리). 최종은 --fast 없이.
FAST = "--fast" in sys.argv[1:]
_jsargs = [a for a in sys.argv[1:] if a.endswith(".js")]
if not _jsargs:
    print("사용: build_ppt.py <build.js> [--fast]"); sys.exit(2)
js = _jsargs[0]

# [0/5] 레퍼런스 확인 — 폴더를 스캔해 강제하던 절차는 폐기했다.
#   참고할 덱·이미지는 그때그때 직접 지정하고, 만드는 사람이 그 이미지를 열어
#   밀도와 눈높이를 맞춘다. 폴더 스캔·반영기록 강제·차단은 전부 없앴다.
print("━━ [0/5] 레퍼런스 = 그때 지정한 이미지를 열어 반영 (폴더 강제 절차 없음) ━━")

# [0/5b] 흰박스 구조 정본 강제 확인
#   "다음에 확인하겠다"는 의지에 맡기면 바쁜 날 제일 먼저 건너뛴다. 그래서 코드로 막는다.
#   기준 덱 = 흰박스 상하규격·좌우가변 구조의 정본(잘 나온 덱을 쌓아두는 개인 폴더).
#   build.js는 이 정본에 흰박스를 어떻게 맞췄는지 한 줄 기록 없이는 통과 못 한다. 형식(build.js 어디든):
#      @whitebox-ref
#      BEST PPT Design: <흰박스 top/height를 이 정본에 맞춘 방식·수치 한 줄 (10자+)>
_PPTREF = os.environ.get("PPT_REFERENCE_DECK",
    os.path.join(os.path.expanduser("~"), "PPT Reference", "BEST PPT Design.pptx"))
#   ↑ 잘 나온 덱을 쌓아두는 개인 정본 폴더. 환경변수 PPT_REFERENCE_DECK로 바꿀 수 있다.
#     파일이 없으면 이 게이트는 통과한다(개인 자산이라 번들에 없음).
print("━━ [0/5b] 흰박스 구조 정본 확인 (BEST PPT Design.pptx — 상하규격 정본) ━━")
if os.path.isfile(_PPTREF):
    _js_wb = unicodedata.normalize("NFC", open(js, encoding="utf-8").read())
    _wb_idx = _js_wb.find("@whitebox-ref")
    _wb_block = _js_wb[_wb_idx:] if _wb_idx >= 0 else ""
    _wb_ok = bool(re.search(r'BEST PPT Design\s*[:：\-—]\s*(\S.{9,})', _wb_block))
    if _wb_idx < 0 or not _wb_ok:
        print(f"\n❌ PPT 미완성 — 흰박스 정본 반영기록 누락(코드 강제).")
        print(f"   🚨 정본을 Read로 열어 흰박스 상하규격(top·height)을 눈에 넣고, build.js에 아래 블록을 넣어라:")
        print(f"      정본: {_PPTREF}")
        print(f"      // @whitebox-ref")
        print(f"      //   BEST PPT Design: 흰박스 top/height를 이 정본에 맞춤 — <수치·방식 한 줄>")
        sys.exit(1)
    print("   ✅ 흰박스 정본 반영기록 확인 — 통과.")
else:
    print(f"   (흰박스 정본 없음: {_PPTREF} — 통과. 개인 자산이라 번들에 없다)")

# [1/4] 카피 게이트 — 카피 원칙 (제작자 즉흥 카피 차단)
#   🚨 PPT 카피(슬라이드의 모든 글자)는 카피 담당이 먼저 쓴다. build.js의 한글 문자열을
#   추출해 brandlogy_lint로 강제 검사 — ERROR면 빌드 자체를 막는다.
print(f"━━ [1/5] brandlogy_lint (슬라이드 카피 — 카피 담당이 먼저) ━━")
_src = open(js, encoding="utf-8").read()
_copies = re.findall(r'"([^"]*[가-힣][^"]*)"|\'([^\']*[가-힣][^\']*)\'|`([^`]*[가-힣][^`]*)`', _src)
_copy_text = "\n".join(x for tup in _copies for x in tup if x)
_copy_tmp = os.path.join(TMP, "_ppt_copy.txt")
open(_copy_tmp, "w", encoding="utf-8").write(_copy_text)
_bl = subprocess.run([PY, os.path.join(HERE, "brandlogy_lint.py"), _copy_tmp])
if _bl.returncode != 0:
    print("\n❌ PPT 미완성 — 슬라이드 카피가 brandlogy_lint ERROR.")
    print("   🚨 카피는 제작자 즉흥 작성 금지. 카피 담당이 먼저 쓰고(보이스·So what·메타포 없이 한 번에 이해),")
    print("      솔직히·줄표·이모지·대조말투를 0으로 고쳐 다시 빌드. (PPT = 디자인 + 카피 협업)")
    sys.exit(1)

print(f"\n━━ [2/5] node {os.path.basename(js)} ━━")
r = subprocess.run(["node", js], capture_output=True, text=True)
sys.stdout.write(r.stdout)
if r.stderr.strip(): sys.stderr.write(r.stderr)
if r.returncode != 0:
    print("❌ 빌드(node) 실패 — 위 에러 수정 후 다시."); sys.exit(1)

# pptx 경로 추출 (빌드 스크립트가 'Saved: <경로>' 또는 '완료 ...: <경로>' 출력)
#)만 매치해, 정본 템플릿처럼 상대경로(예: "샘플-발표자료-v01.pptx")를
#   출력하는 스크립트는 경로를 못 찾아 정상 빌드가 도리어 차단됐다. → 슬래시를 옵셔널로 + abspath 정규화.
m = re.search(r'(?:Saved:|완료[^\n]*?:)\s*(/?[^\n]+?\.pptx)', r.stdout)
if not m:
    print("❌ 빌드 출력에서 pptx 경로를 못 찾음 (스크립트가 'Saved: <경로>'를 출력해야 함)."); sys.exit(1)
pptx = os.path.abspath(m.group(1).strip())
if not os.path.isfile(pptx):
    print(f"❌ 빌드 출력 경로의 pptx가 실제로 없음: {pptx}"); sys.exit(1)

print(f"\n━━ [3/5] ppt_lint (코드 강제 검사) ━━")
lint = subprocess.run([PY, os.path.join(HERE, "ppt_lint.py"), js, pptx])
if lint.returncode != 0:
    print("\n❌ PPT 미완성 — ppt_lint ERROR. 0으로 고쳐 다시 빌드하기 전엔 '완료' 보고 금지. (PNG·open 단계 차단)")
    sys.exit(1)

print(f"\n━━ [4/5] soffice PNG QA 생성 (레이아웃·밀도·정렬용 — 카드 글자 위치 정본은 [5/5] 실렌더) ━━")
base = os.path.splitext(os.path.basename(pptx))[0]
try:
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", TMP, pptx],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except FileNotFoundError:
    print("   ⚠️ soffice(LibreOffice) 없음 — PNG QA 스킵. pptx로 직접 열어 확인할 것.")
pdf = os.path.join(TMP, f"{base}.pdf")
if os.path.exists(pdf):
    try:
        subprocess.run(["pdftoppm", "-png", "-r", "130", pdf, os.path.join(TMP, f"{base}_qa")],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("   ⚠️ pdftoppm 없음 — PNG 변환 스킵.")
    pngs = sorted([f for f in os.listdir(TMP) if f.startswith(f"{base}_qa")])
    print(f"✅ ppt_lint 통과 + PNG {len(pngs)}장 생성: {os.path.join(TMP, base + '_qa-*.png')}")
    print("   → 다음: PNG를 눈으로 확인(겹침·정렬·밀도·흰박스안흰박스·색 계열색), 통과하면 open으로 띄운다.")
    print("   📋 카피 자문: 이 슬라이드 글자(헤드라인·서브·칩·하단 띠)를 카피 보이스로 '먼저' 썼는가? 제작자 즉흥 X (team-brandlogy-writing-dept)")
    print("   📋 하단 띠 라벨 자문: 'SO WHAT' 고정이 아니라 슬라이드 성격에 맞게 가변했는가? (핵심·한 줄 정리·이번 강 한마디 등, 디자인 형식만 유지하고 말은 가변)")
    print("   📋 시각밀도 자문: 박스+글자만 아니라 숫자(KPI)·미니차트·인포그래픽으로 채웠는가? (검증된 실제 수치만, 환각 X — ppt-no-design-laziness)")
    print("   📋 시각화 탐색 자문(): 이 슬라이드에 '고려한 시각화 옵션'을 최소 3개 떠올렸는가 — 사진·아이콘·메타포 도식(저울·벤·사이클 등)·다이어그램·인포그래픽 중. 검증된 도형(노드·박스·칩)으로 '자동 회귀'한 건 아닌가?(standing 습관 경계) ※ 단 차트는 실제 수치 있을 때만 — 신뢰도·만족도 등 없는 숫자 지어내 차트화 금지(환각). '다양성=차트 욱여넣기' 아님. 그리고 다양성은 fit 우선 — 저울·벤·타임라인·사진은 노드비교보다 '메시지를 더 잘 보여줄 때만'. 안 어울리는 다이어그램 장식 욱여넣기는 반대쪽 실패(다양성은 fit에 봉사, 체크박스 아님).")
    print(f"   파일: {pptx}")
    # 🔍 외부 삽입 이미지(배경 외)가 있으면 → QA PNG를 4분할 크롭해 자동 저장. '통짜로만 보기' 차단.
    #    실제로 터진 자리: 끝노드에서 번호가 아바타에 가려졌는데 통짜 이미지만 보고 "겹침 0"으로 오판했다.
    #    확대 스크린샷에서야 드러났다. 그래서 외부 이미지가 있으면 크롭을 들이밀어 밀집부를 강제로 보게 한다.
    _n_img = len(re.findall(r'\.addImage\(', _src))
    if _n_img >= 2:   # 배경 + 최소 1개 외부 이미지
        try:
            from PIL import Image as _PILImage
            _qa0 = os.path.join(TMP, f"{base}_qa-1.png")
            if os.path.exists(_qa0):
                _im = _PILImage.open(_qa0); _W, _H = _im.size
                _cells = {"좌상": (0, 0, 0.52, 0.58), "우상": (0.48, 0, 1.0, 0.58),
                          "좌하": (0, 0.42, 0.52, 1.0), "우하": (0.48, 0.42, 1.0, 1.0)}
                _saved = []
                for _nm, (x0, y0, x1, y1) in _cells.items():
                    _p = os.path.join(TMP, f"{base}_crop_{_nm}.png")
                    _im.crop((int(_W*x0), int(_H*y0), int(_W*x1), int(_H*y1))).save(_p)
                    _saved.append(_p)
                print(f"   🔍 외부 이미지 {_n_img-1}개 포함 → 통짜 PNG만 보면 라벨↔이미지 겹침을 놓친다(끝노드에서 터진 사고).")
                print(f"      아래 4분할 크롭을 '각각 단독 Read'해 요소 밀집부 겹침을 확인하기 전엔 '완료' 보고 금지:")
                for _p in _saved: print(f"        {_p}")
        except Exception as _ce:
            print(f"   (크롭 QA 생성 실패: {_ce} — 외부 이미지를 PIL 크롭으로 수동 확인할 것)")
else:
    print(f"✅ ppt_lint 통과 (PNG 변환 실패 — soffice 수동 확인). 파일: {pptx}")

# ━━ [5/5] 실제 PowerPoint 실렌더 QA ━━
# 🎯 soffice(LibreOffice)는 pptxgenjs addText의 폰트 메트릭·줄바꿈·auto-fit을 PowerPoint와 다르게
#    렌더한다 → soffice PNG에서 카드 글자가 멀쩡해도 실제 PowerPoint에서 겹치거나 잘릴 수 있다.
#    받는 사람은 결국 PowerPoint에서 연다. 카드 글자(addText)·겹침·잘림의 '정본'은 실제 PowerPoint 실렌더다.
#    같은 지적을 반복해서 받지 않으려고, soffice에서 멈추던 수동 절차를 코드에 박았다.
#    (검증된 osascript: save active presentation ... as save as PDF)
#    ⚠️ PowerPoint 미설치·자동화 권한 없음 등은 빌드를 막지 않는다(soffice QA + ppt_lint로 이미 통과). 경고만.
print(f"\n━━ [5/5] 실제 PowerPoint 실렌더 QA (카드 글자·겹침 정본 — soffice와 다를 수 있음) ━━")
if FAST:
    print("   ⏭️  --fast: 실렌더 스킵(반복 수정 중). 🚨 넘기기 전 최종 빌드는 반드시 --fast 없이 돌려 실렌더로 카드 글자를 확인할 것.")
else:
    real_pdf = os.path.join(TMP, f"{base}_realppt.pdf")
    try:
        if os.path.exists(real_pdf): os.remove(real_pdf)
    except Exception: pass
    # 🚨🚨 재발 방지 — 열려 있는 남의 문서와 '교집합 0' 원칙.
    #   1차 사고: 저장하지 않고 앱을 끄게 해서 작업이 통째로 날아갔다.
    #   2차 구멍: 이름을 지정해도, 바로 그 파일을 열어 손보는 중이면 그대로 날아간다
    #            (합격본을 직접 수정하는 건 흔한 작업 방식이다).
    #   해법: 원본을 열지 않는다. 고유 이름의 렌더 전용 임시 복사본만 열고, 그 이름만 닫는다.
    #         → PowerPoint에 이미 열려 있는 어떤 문서와도 이름이 겹칠 수 없다(선제 close 전면 제거).
    # UUID: PID는 재사용되므로 오래 남은 임시 문서와의 이론적 충돌까지 제거(외부 검증)
    _rtmp = os.path.join(TMP, f"__render_{uuid.uuid4().hex[:12]}_{base}.pptx")
    try:
        shutil.copy2(pptx, _rtmp)
    except Exception as _ce:
        _rtmp = None
        print(f"   ⚠️ 렌더용 임시 복사 실패: {_ce}")
    _osa = (
        'tell application "Microsoft PowerPoint"\n'
        '  activate\n'
        '  with timeout of 600 seconds\n'
        f'    open POSIX file "{_rtmp}"\n'
        f'    save presentation "{os.path.basename(_rtmp)}" in (POSIX file "{real_pdf}") as save as PDF\n'
        # 🔒 닫는 대상은 오직 우리가 방금 연 임시 복사본 이름뿐. active/front/quit 금지.
        f'    close (every presentation whose name is "{os.path.basename(_rtmp)}") saving no\n'
        '  end timeout\n'
        'end tell\n'
        'return "PPT_PDF_OK"'
    ) if _rtmp else None
    try:
        _rr = subprocess.run(["osascript", "-e", _osa], capture_output=True, text=True, timeout=200) if _osa else None
    except Exception as _re:
        _rr = None
        print(f"   ⚠️ osascript 실행 실패: {_re}")
    if os.path.exists(real_pdf) and os.path.getsize(real_pdf) > 10000:
        try:
            subprocess.run(["pdftoppm", "-png", "-r", "130", real_pdf, os.path.join(TMP, f"{base}_real")],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            print("   ⚠️ pdftoppm 없음 — 실렌더 PNG 변환 스킵.")
        _real_pngs = sorted(f for f in os.listdir(TMP) if f.startswith(f"{base}_real") and f.endswith(".png"))
        if _real_pngs:
            print(f"   🎯 실제 PowerPoint 실렌더 PNG {len(_real_pngs)}장: {os.path.join(TMP, base + '_real-*.png')}")
            print(f"      → 카드 글자(addText)·겹침·잘림은 soffice PNG가 아니라 이 PowerPoint 실렌더로 '눈으로' 최종 확인한다.")
            print(f"      → 확인 전 '완료' 보고 금지. (외부 삽입 이미지가 있으면 실렌더 PNG도 단독 Read로 밀집부 확인)")
        else:
            print(f"   ⚠️ 실렌더 PDF→PNG 변환 실패 — {real_pdf}를 직접 Read로 확인할 것.")
    else:
        _err = (_rr.stderr.strip()[:200] if _rr and _rr.stderr else "PDF 미생성")
        print(f"   ⚠️ PowerPoint 실렌더 실패(미설치·권한·자동화 차단 가능): {_err}")
        print(f"      → soffice PNG는 addText 위치를 PowerPoint와 다르게 렌더할 수 있다. 넘기기 전 PowerPoint로 직접 열어 카드 글자를 확인할 것.")
        print(f"      🚫 실렌더가 막혀도 앱을 종료하거나 열린 문서를 닫아 뚫지 않는다 — 실패는 실패로 보고한다.")
    # 렌더 전용 임시 복사본 정리(작업이 끝난 뒤 삭제 — 원본과 무관한 /tmp 파일)
    try:
        if _rtmp and os.path.exists(_rtmp): os.remove(_rtmp)
    except Exception: pass

# ━━ 카피 QA: pptx 실제 텍스트 추출 (PNG 아닌 실문자로 오타·깨짐 확인) ━━
#'뼈대'→'빼대') 오타 판정에 못 믿는다.
#   카피 정확성은 PNG 눈 QA가 아니라 pptx <a:t> 실제 텍스트로 확인한다. PNG는 레이아웃 확인용.
import zipfile as _zip, html as _html
print("\n━━ 카피 QA: pptx 실제 텍스트 (PNG 글자깨짐은 렌더 아티팩트일 수 있음 — 오타 판정은 이 실문자로) ━━")
try:
    _z = _zip.ZipFile(pptx)
    for _n in sorted(x for x in _z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$', x)):
        _xml = _z.read(_n).decode('utf-8')
        _ts = [_html.unescape(t) for t in re.findall(r'<a:t>(.*?)</a:t>', _xml, re.S) if t.strip()]
        print(f"  [{_n.split('/')[-1]}] " + " | ".join(_ts))
    print("   → 위 실제 텍스트로 오타·문구를 확인한다(눈 QA PNG의 글자 깨짐에 속지 말 것).")
except Exception as _e:
    print(f"  (텍스트 추출 실패: {_e})")

# ━━ [6/6] 교차검수 안내 (차단 아님) ━━
#   제작자 본인이 자기 결과물을 통과시키는 구조는 두 번 뚫린다. 마지막 판정은 '다른 눈'이 한다.
#   자동 호출은 환경마다 다르므로 이 번들에서는 강제하지 않고 안내만 한다.
#   자기 환경에서 자동화하려면 이 아래에 검수 호출을 붙이고, 실패는 sys.exit(3)으로 막아라.
if not FAST:
    print("\n━━ 🚦 [6/6] 교차검수 (사람이 한다 — 이 단계는 코드가 대신하지 않는다) ━━")
    print("   위 QA PNG와 실제 텍스트를 '만든 사람이 아닌 눈'으로 한 번 더 본다.")
    print("   본다: ① 카드 글자 잘림·겹침 ② 슬라이드마다 레이아웃 판이 다른가 ③ 수치·오타 ④ 카피가 So what까지 닿았나")
    print("   통과 전에는 '완료'라고 부르지 않는다.")

print("\n✅ 빌드 완료:", pptx)
