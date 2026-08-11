#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ppt_lint.py — 페이퍼로지/클로드 PPT 빌드 규칙 "코드 강제" 린터 (전 원칙 코드화판)
# 빌드 JS 소스 + 생성된 pptx를 검사해, PPT 디자인 원칙을 빠짐없이 확인한다.
#   ERROR 1건이라도 있으면 exit 1  → 이 PPT는 "완료"라 보고 금지(고쳐 통과시킬 것).
#   WARN 은 코드로 단정 못 하는 것(오탐 가능) → 빌드 후 PNG로 반드시 눈 확인.
# 사용: python3 ppt_lint.py <build.js> [output.pptx]
import sys, re, os, zipfile, math

if len(sys.argv) < 2:
    print("사용: ppt_lint.py <build.js> [output.pptx]"); sys.exit(2)
js_path = sys.argv[1]
pptx = sys.argv[2] if len(sys.argv) > 2 else None
js = open(js_path, encoding='utf-8').read()
js_nc = re.sub(r'//.*', '', js)   # 주석 제거

# 생성 pptx 슬라이드 본문 텍스트 (가장 정확한 검사 대상)
slide_text = ""
if pptx and os.path.exists(pptx):
    with zipfile.ZipFile(pptx) as z:
        for n in sorted(z.namelist()):
            if re.match(r'ppt/slides/slide\d+\.xml$', n):
                xml = z.read(n).decode('utf-8', 'ignore')
                slide_text += ' '.join(re.findall(r'<a:t>(.*?)</a:t>', xml, re.S)) + ' '
T = slide_text if slide_text.strip() else js_nc
src = "pptx 슬라이드 본문" if slide_text.strip() else "JS 소스(주석 제외)"

errors, warns = [], []

# 0b. 슬라이드 내 도형 id(cNvPr) 중복 = PowerPoint "복구" 창 유발 → 차단
#   pptxgenjs가 s.slideNumber placeholder id를 25로 하드코딩해, 도형 25개 넘는
#   밀도 슬라이드에서 자동번호 도형과 충돌한다. fix-slidenum.py가 dedup하지만,
#   그게 누락돼도 여기서 잡아 "완료" 보고를 막는다.
if pptx and os.path.exists(pptx):
    with zipfile.ZipFile(pptx) as z:
        for n in sorted(z.namelist()):
            if re.match(r'ppt/slides/slide\d+\.xml$', n):
                _xml = z.read(n).decode('utf-8', 'ignore')
                _ids = re.findall(r'<p:cNvPr id="(\d+)"', _xml)
                _dup = sorted(set(i for i in _ids if _ids.count(i) > 1), key=int)
                if _dup:
                    errors.append(f"{os.path.basename(n)} 도형 id 중복 {_dup} — "
                                  f"PowerPoint '복구' 창 유발. fix-slidenum.py의 id 재배정이 안 돎(호출 확인).")

# ───────── ERROR (명확·차단) ─────────
# 1. 줄표
if '—' in T: errors.append("줄표 em dash(—) → 콜론(:)·쉼표(,)·물결(~)로")
if '–' in T: errors.append("줄표 en dash(–) → 물결(~)·콜론으로")
# 2. 원형숫자
circ = sorted(set(re.findall(r'[①-⑳⓪❶-❿㉑-㉟]', T)))
if circ: errors.append(f"원형숫자 {''.join(circ)} → 도형 원+일반숫자(1·2·3)")
# 3. 이모지 (📁 💬 만 허용)
ALLOW_EMOJI = {'\U0001F4C1', '\U0001F4AC'}
emo = re.findall(r'[\U0001F000-\U0001FAFF☀-⛿✀-➿⌀-⏿⬀-⯿❢-❧]', T)
bad = sorted(set(e for e in emo if e not in ALLOW_EMOJI))
if bad: errors.append(f"이모지 {' '.join(bad)} → 📁💬만 허용, 나머지 제거")
# 4. 자동 슬라이드번호 — 주석 제외(js_nc)로 본다. "// slideNumber 나중에 추가" 같은 코멘트만으로
#    실제 호출이 없어도 통과되던 구멍(5·6도 동일 이유로 js_nc로 통일).
if 'slideNumber' not in js_nc: errors.append("s.slideNumber 자동 슬라이드번호 누락 (고정텍스트 번호 금지)")
# 5. fix-slidenum
if 'fix-slidenum' not in js_nc: errors.append("fix-slidenum.py 호출 누락 (writeFile().then())")
# 6. 배경 이미지
if 'Background_' not in js_nc: errors.append("배경 이미지(Background_paperlogy) addImage 누락")
# 6b. 클로드 프로젝트 색·배경 전면 금지 "클로드 프로젝트 끝났어. 클로드 색깔 하지마" — 우리 원칙=클라인 블루)
#   코랄만 잡던 구멍과 본문 HTML 미검사 구멍을 함께 막는다 → 폐기색 전체 블랙리스트 + build.js·본문HTML 양쪽 스캔.
CLAUDE_DEAD = {'D97757','292524','6B6862','F4F2EE','8A8378','DAD6CE','E7E2DE','F4EEE8',
               'D9A38D','A8A29E','8B857D','C8BEB4'}  # 클로드 강의 코랄·차콜·웜그레이·웜화이트·베이지 계열 전체
if 'Background_claudelogo' in js:
    errors.append("🚫 Background_claudelogo 금지 — 클로드 프로젝트 종료. 배경은 Background_paperlogy.jpg만.")
_scan = [('build.js', js)]
_mh = re.search(r'BODY_HTML[:\s]+["\']?([^\s"\'\)]+\.html)', js)
if _mh:
    _html_path = _mh.group(1)
    if not os.path.isabs(_html_path):
        _html_path = os.path.join(os.path.dirname(os.path.abspath(js_path)), _html_path)
    if not os.path.exists(_html_path):
        errors.append(f"본문 HTML 검사 실패: BODY_HTML 경로가 없음 ({_html_path})")
    else:
        try:
            with open(_html_path, encoding='utf-8') as _f: _scan.append(('본문HTML', _f.read()))
        except Exception as _e:
            errors.append(f"본문 HTML 검사 실패: {_html_path} ({_e})")
elif re.search(r'/tmp/\S*body\S*\.png', js) and not _mh:
    errors.append("본문 HTML을 addImage(PNG)로 넣는데 'BODY_HTML: <경로>' 주석이 없어 색 검사를 못 함 — 검사 불능 상태로 빌드 금지.")
for _src, _txt in _scan:
    _dead = sorted(set(h.upper() for h in re.findall(r'["\'#]([0-9A-Fa-f]{6})', _txt)) & CLAUDE_DEAD)
    if _dead:
        errors.append(f"🚫 클로드 폐기색 {len(_dead)}개({', '.join(_dead)}) in {_src} — 클로드 프로젝트 종료. 클라인 블루(002FA7/001C64)·오렌지(FF7A00 비문자)·페이퍼로지 중립만.")
# 7. 로고 텍스트 추가 금지 (배경에 이미 있음)
if re.search(r'addText\(\s*[`"\'][^`"\')]*brandlogy', js, re.I):
    errors.append("로고 텍스트 'brandlogy' addText — 배경에 이미 있으니 추가 금지")
# 8. 모든 차트에 수치 표기 (showValue/showPercent)
n_chart = len(re.findall(r'\.addChart\(', js))
if n_chart:
    n_val = len(re.findall(r'show(?:Value|Percent)\s*:\s*true', js))
    if n_val < n_chart:
        errors.append(f"차트 {n_chart}개 중 수치표기(showValue/showPercent:true) {n_val}개 — 모든 차트에 수치 필요")
# 8b. 폐기된 옛 블루 팔레트
OLD_BLUE = {'4F6EF1','0014D3','7E94F5','A8B7F8','DDE3FB','F8F9FF',  # 옛 형광블루 ( 폐기)
            '1C6DD0','0B2E4F','5B9BD5','A9C9E8','DBE9F6','F1F6FB'}  # 옛 딥네이비/메디컬블루 ( 폐기)
# CLAUDE_DEAD(6b)처럼 닫는 따옴표를 요구하지 않는다("background:#4F6EF1;"처럼 뒤에 문자가
# 붙는 CSS 값은 놓친다) 및 build.js뿐 아니라 본문HTML(_scan)까지 같이 본다 — 6b와 같은 구멍.
used_old = sorted({h.upper() for _src, _txt in _scan for h in re.findall(r'["\'#]([0-9A-Fa-f]{6})', _txt)} & OLD_BLUE)
if used_old:
    errors.append(f"폐기된 옛 블루 {', '.join(used_old)} — 표준은 클라인 블루(brand 002FA7 / brandDeep 001C64 / accent FF7A00).")
# 8f. 강조 오렌지 FF7A00 = 비문자 요소 전용(탭·바·면·밑줄) — 글자·숫자엔 크기 무관 금지
#     G 대형 3:1 미달. 승인 시안 A도 오렌지=탭뿐. 텍스트 강조는 brand/brandDeep)
for m in re.finditer(r'addText\s*\(', js):
    depth, i = 0, m.end() - 1
    while i < len(js):
        if js[i] == '(': depth += 1
        elif js[i] == ')':
            depth -= 1
            if depth == 0: break
        i += 1
    call = js[m.start():i]
    if re.search(r'color:\s*["\'](?:#)?FF7A00', call, re.I) or re.search(r'\bcolor:\s*C\.accent\b', call):
        snippet = re.sub(r'\s+', ' ', call[:60])
        errors.append(f"강조 오렌지 FF7A00을 글자색으로 사용({snippet}…) — 오렌지는 탭·바·면 등 비문자 전용, 텍스트 강조는 brand 002FA7/brandDeep 001C64 (대비 ~2.4:1 WCAG 미달, )")
    elif 'FF7A00' in call.upper():
        warns.append("addText 안에 FF7A00(fill 추정) — 오렌지 면 위 글자 대비 눈 확인 (흰 글자도 2.7:1로 약함)")
# 8c. 화살표(연결선)가 카드 박스 경계를 침범(겹침) —"화살표랑 박스끼리 겹친다")
#     box() 카드 사각형과, endArrowType 달린 line(화살표)의 x구간이 교차하되 박스에 완전 포함이 아니면 = 경계 가로지름 = 겹침.
#     화살표는 박스 사이 gap 안에만 두거나, 박스 안에 완전히 넣을 것. (gap·완전포함은 통과 → 오탐 최소)
_boxes = [tuple(map(float, m.groups()))
          for m in re.finditer(r'box\(\s*\w+\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)', js_nc)]
_overlaps = []
for _m in re.finditer(r'ShapeType\.line\b', js_nc):
    _seg = js_nc[_m.start(): _m.start() + 280]
    if 'endArrowType' not in _seg:
        continue
    _xm = re.search(r'x:\s*([\d.]+)', _seg); _ym = re.search(r'y:\s*([\d.]+)', _seg); _wm = re.search(r'w:\s*([\d.]+)', _seg)
    if not (_xm and _wm):
        continue
    _ax = float(_xm.group(1)); _aw = float(_wm.group(1)); _ax2 = _ax + _aw
    _ay = float(_ym.group(1)) if _ym else None
    for (_bx, _by, _bw, _bh) in _boxes:
        _bx2 = _bx + _bw
        if _ay is not None and not (_by - 0.10 <= _ay <= _by + _bh + 0.10):
            continue
        _x_cross = _ax < _bx2 and _ax2 > _bx
        _fully_in = _ax >= _bx - 0.001 and _ax2 <= _bx2 + 0.001
        if _x_cross and not _fully_in:
            _overlaps.append((_ax, _ax2, _bx, _bx2))
if _overlaps:
    _a = _overlaps[0]
    errors.append(f"화살표가 카드 박스 경계를 침범(겹침) {len(_overlaps)}건 "
                  f"(예: 화살표 x{_a[0]:.2f}~{_a[1]:.2f} vs 박스 x{_a[2]:.2f}~{_a[3]:.2f}) "
                  f": 화살표는 박스 사이 gap 안에만 두거나 박스 안에 완전히 넣을 것 ( 반복 지적)")
# 8d. 원(불릿/도트)과 옆(또는 안) 텍스트의 세로 중심 불일치 —"저 원은 왜 텍스트랑 정렬을 안 맞춰? 자주 그러던데"
#     원(ellipse)은 top기준 작은 높이(예 0.15), 옆 텍스트는 valign:middle 큰 박스(예 0.50)에 둠.
#     원 y를 손으로 'ey+0.05'처럼 임의 오프셋 주면 → 원중심(y+h/2) ≠ 텍스트중심(y+h/2)으로 어긋남(원이 위/아래로 뜸).
#     같은 y베이스(같은 변수 또는 둘 다 숫자)면 (상수오프셋 + h/2)만 비교해 세로중심 일치를 검사. 차이>0.04in 이면 차단.
def _yh(seg):
    ym = re.search(r'\by:\s*([A-Za-z_][\w.]*)?\s*([+\-])?\s*([\d.]+)?', seg)
    hm = re.search(r'\bh:\s*([\d.]+)', seg)
    if not ym or not hm: return None
    var, sign, num = ym.group(1), ym.group(2), ym.group(3)
    if num is not None and not re.search(r'\d', num): num = None  # 'c.y +0.22' 등에서 잘못 잡힌 '.' 방어
    if var is None and num is None: return None
    const = float(num) * (-1 if sign == '-' else 1) if num is not None else 0.0
    return (var or '__num__', const, float(hm.group(1)))
_mis = []
for _m in re.finditer(r'ShapeType\.ellipse\b', js_nc):
    _ey = _yh(js_nc[_m.start(): _m.start() + 220])
    if not _ey: continue
    _tm = re.search(r'\.addText\(', js_nc[_m.end(): _m.end() + 340])  # 직후 가장 가까운 텍스트(같은 줄 묶음)
    if not _tm: continue
    _ts = _m.end() + _tm.start()
    _tseg = js_nc[_ts: _ts + 380]
    if not re.search(r'valign:\s*["\'](?:middle|center)', _tseg): continue  # 중앙정렬 텍스트만(top=baseline 의도 제외)
    _ty = _yh(_tseg)
    if not _ty or _ey[0] != _ty[0]: continue                 # 같은 y베이스일 때만 비교(오탐 차단)
    _delta = (_ey[1] + _ey[2] / 2) - (_ty[1] + _ty[2] / 2)   # 원 세로중심 − 텍스트 세로중심
    if abs(_delta) > 0.04:
        _mis.append(round(_delta, 3))
if _mis:
    errors.append(f"원(불릿/도트)과 옆 텍스트 세로중심 어긋남 {len(_mis)}건 (원중심−텍스트중심 Δ{_mis[0]:+.3f}in) "
                  f": 원 y를 '(텍스트y) + (텍스트h)/2 − (원h)/2'로 맞춰 두 세로중심을 일치시킬 것 "
                  f"( '저 원 왜 텍스트랑 정렬 안 맞아, 자주 그런다')")
# 8e. 텍스트가 삽입 이미지 위에 겹침 —"붙어서 겹치는 건 하지 마, 디자인 기본이잖아"
#     좌표 변수(const CX=0.42 …)를 심볼테이블로 풀어, addImage(배경·목업 제외) 박스와 addText 박스가
#     가로 60%+ AND 세로 0.2in+ 둘 다 겹치면 = 의도밖 겹침 → ERROR. (평가 안 되는 복잡식 좌표는 skip해 오탐 0 지향)
_sym = {}
def _num(expr):
    # 숫자 리터럴/변수/일반 산술(+ - * / 괄호, 알려진 심볼)까지 평가. 못 풀면 None.
    if expr is None: return None
    expr = expr.strip().rstrip(',')
    if expr == '' or not re.fullmatch(r'[-+*/().\s\w]+', expr): return None
    def _rep(m):
        t = m.group(0)
        if re.fullmatch(r'-?\d+\.?\d*', t): return t
        return str(_sym[t]) if t in _sym else 'None'
    e2 = re.sub(r'[A-Za-z_]\w*|\d+\.?\d*', _rep, expr)
    if 'None' in e2 or not re.fullmatch(r'[-+*/().\d\s]+', e2): return None
    try:
        return float(eval(e2, {"__builtins__": {}}, {}))
    except Exception:
        return None
# 숫자 const 심볼 다중패스 (변수·산술 우변까지: RXc = LXc + LW + GAP, HH = 2.10 등)
for _ in range(6):
    for _m in re.finditer(r'\b([A-Za-z_]\w*)\s*=\s*([-+*/().\w\s]+?)\s*(?=[,;\n])', js_nc):
        _nm, _rhs = _m.group(1), _m.group(2)
        if _nm in _sym: continue
        _v = _num(_rhs)
        if _v is not None: _sym[_nm] = _v
def _opt(seg, key):
    m = re.search(rf'\b{key}:\s*([^,}}\n]+)', seg)
    return _num(m.group(1)) if m else None
_strsym = {}   # 문자열 const (path: BG 처럼 변수로 주는 경로를 실제 값으로 풀기 위함)
for _m in re.finditer(r'\b([A-Za-z_]\w*)\s*=\s*["\']([^"\']+)["\']', js_nc):
    _strsym.setdefault(_m.group(1), _m.group(2))
_shapealias = {}   # 도형 약칭 (const RR = pres.ShapeType.roundRect → RR:roundRect)
for _m in re.finditer(r'\b(\w+)\s*=\s*pres\.ShapeType\.(\w+)', js_nc):
    _shapealias.setdefault(_m.group(1), _m.group(2))
def _shape_st(first):
    return first.split('.')[-1] if 'ShapeType.' in first else _shapealias.get(first)
def _collect_imgs(txt):
    out = []
    for _m in re.finditer(r'\.addImage\(\s*\{', txt):
        seg = txt[_m.end() - 1: _m.end() + 280]
        pm = re.search(r'path:\s*([^,}\n]+)', seg)
        praw = pm.group(1).strip() if pm else ""
        p = praw.strip('"\'') if praw[:1] in '"\'' else _strsym.get(praw, praw)   # 변수면 값으로 치환
        if ('Background_' in p) or ('mockup' in p.lower()) or ('목업' in p): continue
        x, y, w, h = _opt(seg, 'x'), _opt(seg, 'y'), _opt(seg, 'w'), _opt(seg, 'h')
        if None not in (x, y, w, h): out.append((x, y, w, h, os.path.basename(p)))
    return out
def _collect_txts(txt):
    out = []
    for _m in re.finditer(r'\.addText\(', txt):
        seg = txt[_m.end(): _m.end() + 560]
        x, y, w, h = _opt(seg, 'x'), _opt(seg, 'y'), _opt(seg, 'w'), _opt(seg, 'h')
        if None not in (x, y, w, h): out.append((x, y, w, h))
    return out
_imgs = _collect_imgs(js_nc)   # WARN 18(외부 삽입 이미지 단독 QA)용 — 전체 이미지
# 겹침 검사는 슬라이드별로(addSlide() 기준 분할) — 다른 슬라이드의 텍스트↔이미지 좌표 오탐 방지
_tov = []
for _chunk in re.split(r'\.addSlide\(\)', js_nc):
    _ci, _ct = _collect_imgs(_chunk), _collect_txts(_chunk)
    for (ix, iy, iw, ih, nm) in _ci:
        if iw > 11.0: continue   # 본문 전체폭 배경 인포그래픽(곡선·면적 등) 위 라벨은 정상 — 겹침 오탐 제외
        for (tx, ty, tw, th) in _ct:
            ox = min(ix + iw, tx + tw) - max(ix, tx)
            oy = min(iy + ih, ty + th) - max(iy, ty)
            if ox > 0.6 * min(iw, tw) and oy > 0.2:
                _tov.append((nm, round(oy, 2)))
if _tov:
    errors.append(f"텍스트가 삽입 이미지 위에 겹침 {len(_tov)}건 (예: {_tov[0][0]} 세로겹침 {_tov[0][1]}in) "
                  f": 텍스트와 이미지는 붙이지 말 것(여백 확보). 캡션·라벨은 이미지 밖에. ( '디자인 기본')")

# 8f. 카드(흰 박스) 안 '큰 단일 이미지'의 중앙정렬 —"흰 박스 안 정렬 안 맞는 거,
#     시간막대가 +0.3 오프셋 때문에 카드 중앙에서 오른쪽으로 쏠린 적이 있다.
#     카드 안에 콘텐츠 이미지가 '1개'뿐이고 그게 카드 폭 절반 이상이면 = 중앙정렬 의도 → 중심 x 어긋나면 ERROR.
#     (좌측 작은 이미지=비중앙 의도 가능하므로 iw>카드폭*0.5 일 때만 검사 → 오탐 0 지향)
def _collect_rr(txt):
    out = []
    # (a) addShape(RR, {x,y,w,h}) 직접 좌표
    for _m in re.finditer(r'\.addShape\(\s*([\w.]+)\s*,\s*\{', txt):
        if _shape_st(_m.group(1)) != 'roundRect': continue
        seg = txt[_m.end() - 1: _m.end() + 320]
        x, y, w, h = _opt(seg, 'x'), _opt(seg, 'y'), _opt(seg, 'w'), _opt(seg, 'h')
        if None not in (x, y, w, h): out.append((x, y, w, h))
    # (b) card(s,x,y,w,h)/box(s,x,y,w,h) 헬퍼 호출부 — 헬퍼 안 addShape는 x,y,w,h가 변수라 (a)로 못 읽음
    for _m in re.finditer(r'\b(?:card|box)\(\s*s\s*,\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,)]+)', txt):
        vals = [_num(_m.group(i)) for i in range(1, 5)]
        if None not in vals: out.append(tuple(vals))
    return out
for _chunk in re.split(r'\.addSlide\(\)', js_nc):
    _cards = [c for c in _collect_rr(_chunk) if c[2] > 5.0]   # 큰 카드만
    _cimg = _collect_imgs(_chunk)
    for (cx_, cy_, cw_, ch_) in _cards:
        _ins = [im for im in _cimg if im[0] >= cx_ - 0.1 and im[0] + im[2] <= cx_ + cw_ + 0.1
                and im[1] >= cy_ - 0.1 and im[1] + im[3] <= cy_ + ch_ + 0.1]
        if len(_ins) == 1 and _ins[0][2] > cw_ * 0.5:
            ix, iy, iw, ih, nm = _ins[0]
            _d = abs((ix + iw / 2) - (cx_ + cw_ / 2))
            if _d > 0.2:
                errors.append(f"카드 안 큰 이미지({nm})가 카드 중앙에서 {_d:.2f}in 어긋남 — 흰 박스 안 정렬은 정확히 중앙(또는 의도 축)에. 이미지 x=(슬라이드폭−iw)/2 또는 카드중심 기준으로 맞춰라 ( '절대 금지').")

# ───────── WARN (코드로 단정 못 함 → PNG/눈 확인) ─────────
# 9. 카드 라인 0 (roundRect에 line color+width = 라인 박음, 차트 축선 제외)
shape_lines = [s for s in re.findall(r'line:\s*\{\s*color[^}]*width[^}]*\}', js_nc) if 'Axis' not in s]
if shape_lines:
    warns.append(f"도형 line(color+width) {len(shape_lines)}곳 — 카드는 line:{{type:'none'}}+그림자만 (차트 축선만 예외)")
# 10. 헤드라인 26pt(채팅 24pt)
if not re.search(r'fontSize:\s*2[46]\b', js):
    warns.append("헤드라인 26pt(채팅장면 24pt)가 안 보임 — 헤더 폰트 확인")
# 11. 대제목 마침표 자동 로직
if '/[.?!]$/' not in js:
    warns.append("대제목 마침표 자동(/[.?!]$/) 로직 없음 — 헤드라인이 마침표·존댓말 평서문으로 끝나는지")
# 12. 헤더 챕터 'NN · 카테고리'
if not re.search(r'\d{2}\s*·', T):
    warns.append("헤더 챕터 'NN · 카테고리'(두 자리+가운뎃점) 형식이 안 보임")
# 13. SO WHAT 띠
if ('SO WHAT' not in js) and ('soWhat' not in js):
    warns.append("SO WHAT 띠가 안 보임 (표지·전환이면 생략 가능, 그 외엔 형식 유지)")
# 14. 색 계열색·틴트 (허용 팔레트 외 hex)
CLAUDE4 = set()   # 클로드 프로젝트 종료() — 클로드 강의 4색(코랄 등) 폐기. 코랄 D97757은 6b에서 ERROR 차단
BLUE = {'002FA7','001C64','4D6DC1','99ACDB','D9E0F2','EAEEF8','FF7A00'}  # 클라인 블루 + 강조 오렌지 ( A안, 옛 딥네이비는 8b ERROR로 이동)
NEUTRAL = {   # (클로드 웜톤 8A8378·DAD6CE·E7E2DE 제거 —  클로드 프로젝트 종료, CLAUDE_DEAD로 이동)
           'FFFFFF','000000','222222','3A4654','5A6678','8A94A2','5F6B78','EFF2F6','F4F6F9',
           'B7BDC8','D5DAE3','F0F0F0','404040','45515E','8E8E93','5F5F5F','F2F3F5',
           'DDE1E8','EEF0F4','F6F7FB','EEEEEE','DCE3EC','ECEEF2','D0D5DD','8E8E93'}
ALLOWED = CLAUDE4 | BLUE | NEUTRAL
# 6b/8b와 같은 이유로 닫는 따옴표를 요구하지 않고, build.js뿐 아니라 본문HTML(_scan)도 같이 본다.
hexes = {h.upper() for _src, _txt in _scan for h in re.findall(r'["\'#]([0-9A-Fa-f]{6})', _txt)}
extra = sorted(h for h in hexes if h not in ALLOWED)
def _is_blue_tint(h):   # 파란 계열(블루 채널 확연 우세) = 즉석 지어낸 블루 틴트
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return b > r + 16 and b > g + 8
_blue_extra = [h for h in extra if _is_blue_tint(h)]
_neut_extra = [h for h in extra if not _is_blue_tint(h)]
if _blue_extra:   #  즉석 블루 틴트가 WARN으로 새던 구멍 → ERROR 격상
    errors.append(f"허용 팔레트 외 '파란 계열 틴트' {len(_blue_extra)}개({', '.join(_blue_extra)}) — 즉석 hex 금지. "
                  f"블루는 002FA7/001C64/4D6DC1/99ACDB/D9E0F2/EAEEF8만. ERROR 0 전 '완료' 보고 금지.")
if _neut_extra:
    warns.append(f"허용 팔레트 외 중립색 {len(_neut_extra)}개({', '.join(_neut_extra[:6])}{'…' if len(_neut_extra)>6 else ''}) — 중립 팔레트로 통일 (눈 확인)")
# 15. 박스 왼쪽 세로 컬러바 (얇고 긴 세로 rect)
if re.search(r'w:\s*0\.0?[0-9]\d?\b[^}]*h:\s*[1-9]', js_nc) or re.search(r'h:\s*[1-9][^}]*w:\s*0\.0?[0-9]\b', js_nc):
    warns.append("얇은 세로 막대(w<0.15·h>1) 의심 — 박스 왼쪽 세로 컬러바 금지 (눈 확인)")
# 16. 파일명 vNN
base = os.path.basename(pptx) if pptx else os.path.basename(js_path)
if not re.search(r'v\d+', base):
    warns.append(f"파일명에 버전(vNN)이 없음: {base} — build-vNN / vNN-주제 권장")
# 17. 차트·수치 밀도 (텍스트 박스만 잔뜩·시각화 0 경보) —"한 장이라고 차트·도식 대충 빼지 마라(반복 지적)"
#     '시각화' = 차트(addChart) OR 외부 삽입 이미지(차트/그래프 PNG) OR 도식 화살표(endArrowType 분기·플로우).
#     ⚠️ 카드(roundRect)+텍스트만으로는 시각화로 안 침. "1장 공간 핑계로 차트·도식 생략"이 게으름의 핵심 패턴.
n_addtext = len(re.findall(r'\.addText\(', js_nc))
n_chart2  = len(re.findall(r'\.addChart\(', js_nc))
n_shape   = len(re.findall(r'\.addShape\(', js_nc))
n_arrow   = len(re.findall(r'endArrowType', js_nc))
# 네이티브 차트는 pptx 실물(ppt/charts/chart*.xml)로도 인식 — js 패턴이 놓쳐도(헬퍼 함수·변수 호출) 실물이 정본.
#   '시각화 0'으로 오판 → 차트를 이미지로 굽는 회피 유발. 외부 검증 검출.
#    룰: 게이트가 네이티브 차트를 못 읽으면 그건 게이트 버그다 — 이미지로 위장할 근거가 아니다.)
n_chart_pptx = 0
if pptx and os.path.exists(pptx):
    try:
        with zipfile.ZipFile(pptx) as _zc:
            n_chart_pptx = sum(1 for _n in _zc.namelist() if re.match(r'ppt/charts/chart\d+\.xml$', _n))
    except Exception: pass
n_chart_all = max(n_chart2, n_chart_pptx)
has_viz   = (n_chart_all > 0) or (len(_imgs) > 0) or (n_arrow > 0)   # _imgs=배경 제외 삽입 이미지
if n_addtext >= 8 and not has_viz:
    # 반복 지적된 지점("또 시각화 안함, 게으름") → WARN을 ERROR로 격상. 카드+텍스트+배지만으론 빌드 차단.
    #   '시각화' = 차트(addChart) OR 외부 삽입 이미지(matplotlib/PIL/사진/목업) OR 도식 화살표(분기·플로우).
    #   배지·칩·흰카드(roundRect)는 텍스트 컨테이너일 뿐 시각화 아님. v152가 정확히 이 구멍으로 빠져나감(WARN 묵살).
    errors.append(f"🚨🚨 시각화 0 (addText {n_addtext} / 차트0·삽입이미지0·도식화살표0) = 빌드 차단( ERROR 격상). "
                 f"카드+글자+배지만으론 '대충'이다 — 차트·그래프·메타포 도식(저울·벤·사이클)·인포그래픽·목업·사진 중 "
                 f"최소 1개를 matplotlib/PIL 등 외부 렌더로 제대로 넣어라. '1장이라 공간 없다'는 핑계 금지. "
                 f"표지·전환 슬라이드(addText<8)만 자동 예외. ※ '그냥 PPT 만들어줘'='풀 시각화 디폴트'(ppt-default-full-visualization).")
# 18. 외부 렌더 이미지(matplotlib 차트 등) 박았으면 → 그 이미지 단독 Read QA 필수 )
#     통짜 PPT PNG로는 이미지 '내부'의 라벨↔데이터점·구분선 미세 겹침이 안 보인다(좌표도 코드가 모름).
if _imgs:
    warns.append(f"외부 삽입 이미지 {len(_imgs)}개({_imgs[0][4]} 등) — 통짜 PPT PNG 말고 이 이미지를 '단독'으로 Read해 "
                 f"내부 라벨↔데이터점·구분선·축의 겹침/근접을 눈으로 확인할 것 "
                 f"(차트 내부 라벨이 첫 마커에 붙는 사고가 잦다. 라벨은 데이터와 충분한 여백)")
# 18b. 분기·연결 사선 커넥터(대각선 line) — 엘보 트리 권장 '<' 꺾쇠 지적)
#      엘보 트리 분기는 line이 전부 가로(h:0)/세로(w:0). w·h 둘 다 ≠0 = 사선 = 조잡한 분기 꺾쇠 의심.
_diag = 0
for _m in re.finditer(r'\.addShape\(\s*pres\.ShapeType\.line\b', js_nc):
    _seg = js_nc[_m.end(): _m.end() + 320]
    _dw, _dh = _opt(_seg, 'w'), _opt(_seg, 'h')
    if _dw is not None and _dh is not None and abs(_dw) > 0.03 and abs(_dh) > 0.03:
        _diag += 1
if _diag:
    warns.append(f"대각선 line 도형 {_diag}곳(w·h 둘 다 ≠0) — 분기·연결이면 사선 꺾쇠('<') 금지, "
                 f"엘보 트리(노드 중앙→줄기→수직 분배선→가로 화살표, 화살표는 박스 직전서 멈춤)로 그릴 것 "
                 f"(분기 연결선은 엘보 트리로 그린다). 실제 사선 강조선이면 무시.")
# 19. 카드 하단 과다 여백 (위 쏠림 — 내용이 카드 상단에 몰리고 하단이 빔) —
#     큰 카드(roundRect)별로 카드 안 '내용'(텍스트는 글자수로 줄수 추정한 렌더높이 + 이미지·도형 할당높이)의
#     최하단을 구해, 카드 하단까지 빈 비율이 30% 초과면 위 쏠림. (텍스트 줄수는 근사 → WARN, 크롭 눈 확인)
def _text_render_h(seg, boxw):
    fs = _opt(seg, 'fontSize') or 12
    lsm = _opt(seg, 'lineSpacingMultiple') or 1.0
    cm = re.match(r'\s*("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')', seg)
    if cm:
        content = cm.group(1)[1:-1]
    else:
        am = re.match(r'\s*\[(.*?)\]\s*,\s*\{', seg, re.S)
        content = ''.join(re.findall(r'text:\s*"((?:[^"\\]|\\.)*)"', am.group(1))) if am else ''
    units = sum(1.0 if ord(c) >= 0x1100 else 0.55 for c in content)
    em = fs / 72.0
    per = max(1.0, boxw / (em * 1.02))
    lines = max(1, math.ceil(units / per)) if units else 1
    return lines * em * 1.25 * (lsm if lsm and lsm > 0 else 1.0)
def _content_bottom(txt, card):
    cx, cy, cw, ch = card
    btm = cy
    for _m in re.finditer(r'\.addText\(', txt):
        seg = txt[_m.end(): _m.end() + 900]
        x, y, w, h = _opt(seg, 'x'), _opt(seg, 'y'), _opt(seg, 'w'), _opt(seg, 'h')
        if None in (x, y) or not (cx - 0.1 <= x < cx + cw and cy - 0.1 <= y < cy + ch): continue
        th = _text_render_h(seg, w if w else (cx + cw - x))
        va = re.search(r'valign:\s*["\'](\w+)', seg)
        end = (y + (h + th) / 2.0) if (va and va.group(1) == 'middle' and h) else (y + th)
        btm = max(btm, end)
    for _m in re.finditer(r'\.add(?:Image|Shape|Chart)\(', txt):
        seg = txt[_m.end(): _m.end() + 340]
        x, y, w, h = _opt(seg, 'x'), _opt(seg, 'y'), _opt(seg, 'w'), _opt(seg, 'h')
        if None in (x, y, w, h): continue
        if abs(x - cx) < 0.02 and abs(y - cy) < 0.02 and abs(w - cw) < 0.02: continue  # 카드 자신
        if not (cx - 0.1 <= x < cx + cw and cy - 0.1 <= y < cy + ch): continue
        btm = max(btm, y + h)
    return btm
_cards = []
for _m in re.finditer(r'\.addShape\(\s*([\w.]+)\s*,\s*\{', js_nc):
    if _shape_st(_m.group(1)) != 'roundRect': continue
    _seg = js_nc[_m.end() - 1: _m.end() + 360]
    cx, cy, cw, ch = _opt(_seg, 'x'), _opt(_seg, 'y'), _opt(_seg, 'w'), _opt(_seg, 'h')
    if None in (cx, cy, cw, ch) or cw < 2.5 or ch < 1.4: continue   # 큰 카드만(칩·작은 박스 제외)
    _cards.append((cx, cy, cw, ch))
#     티어: 45% 초과 = 명백 참사 → ERROR 하드 차단(추정 틀려도 빈 게 확실) / 30~45% = WARN+크롭(추정오차 감안).
#     '무시하고 정상 선언'으로 또 빠져나감 — 명백 참사는 빌드를 막아라.)
# pptx가 있으면 슬라이드 실측 좌표로 측정 — roleBox/rule 등 '함수로 그린' 내용도 최종 좌표라 정확.
#   '빔'을 뱉음 → "함수라 FP"가 게이트 무시 핑계로 굳을 위험.
#    pptx 실측으로 그 FP를 원천 제거. pptx 없을 때만 js 추정 폴백.)
_shapes_emu = []
if pptx and os.path.exists(pptx):
    with zipfile.ZipFile(pptx) as _z:
        for _n in _z.namelist():
            if re.match(r'ppt/slides/slide\d+\.xml$', _n):
                _sx = _z.read(_n).decode('utf-8', 'ignore'); _E = 914400.0
                for _mm in re.finditer(r'<p:(sp|pic|graphicFrame)\b.*?</p:\1>', _sx, re.S):
                    _blk = _mm.group(0)
                    _o = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"', _blk)
                    _e = re.search(r'<a:ext cx="(\d+)" cy="(\d+)"', _blk)
                    if not (_o and _e): continue
                    _g = re.search(r'<a:prstGeom prst="(\w+)"', _blk)
                    # 도형 fill hex(spPr 안, txBody 이전 첫 srgbClr) — #24 다크 강조카드 차등 하한용)
                    _pre_tx = _blk.split('<p:txBody', 1)[0]
                    _f = re.search(r'<a:solidFill><a:srgbClr val="([0-9A-Fa-f]{6})"', _pre_tx)
                    _shapes_emu.append((_n, int(_o.group(1))/_E, int(_o.group(2))/_E, int(_e.group(1))/_E, int(_e.group(2))/_E, _g.group(1) if _g else _mm.group(1), _f.group(1).upper() if _f else ''))
if _shapes_emu:   # ── pptx 실측 좌표 기반(정확, 전 슬라이드) ──
    _cards_e = [(sn, x, y, w, h, f) for (sn, x, y, w, h, k, f) in _shapes_emu if k == 'roundRect' and w > 2.5 and h > 1.4]
    for (slide_name, cx, cy, cw, ch, cfill) in _cards_e:
        _btm = cy
        for (sn, x, y, w, h, k, f) in _shapes_emu:
            if sn != slide_name: continue
            if abs(x-cx) < 0.02 and abs(y-cy) < 0.02 and abs(w-cw) < 0.02 and abs(h-ch) < 0.02: continue  # 카드 자신
            if not (cx-0.05 <= x < cx+cw-0.05 and cy-0.05 <= y < cy+ch): continue                          # 카드 안 요소만
            _btm = max(_btm, y + h)
        _where = os.path.basename(slide_name)
        _ratio = ((cy + ch) - _btm) / ch if ch else 0
        if _ratio > 0.45:
            errors.append(f"{_where} 카드(y{cy:.2f}·h{ch:.2f}) 하단 {_ratio*100:.0f}% 빔 — 명백한 위 쏠림(참사 수준, pptx 실측). "
                          f"본문으로 하단까지 채우거나 카드 높이를 줄여 빔을 없애라. ERROR 0 전 '완료' 보고 금지.")
        elif _ratio > 0.30:
            warns.append(f"{_where} 카드(y{cy:.2f}·h{ch:.2f}) 하단 {_ratio*100:.0f}% 빔 — 위 쏠림(pptx 실측). "
                         f"칩·헤드·본문을 세로로 분산하거나 본문을 늘려 채워라. 카드 하단을 크롭 줌으로 눈 확인.")
        # #24(짝 게이트): 반대로 내용이 카드 바닥에 '딱 붙음'(하단 패딩 부족) —"이딴 식으로 하단에 딱 붙여서 디자인"
        #   큰 흰 컨테이너 카드(h>=2.5)는 제외 — 그건 내용이 바닥까지 차는 게 밀도상 정답(#19·#20). 강조·콘텐츠 카드만.
        #   다크 강조카드(fill=brand 002FA7·brandDeep 001C64)는 어두운 배경이라 여백 부족이 더 두드러짐 →
        #   단순 절대하한 하나 0.25in.
        _pad = (cy + ch) - _btm
        _dark24 = cfill in ('002FA7', '001C64')
        if ch < 2.5 and _btm > cy and _dark24 and _pad < 0.25:
            errors.append(f"{_where} 다크 강조카드(y{cy:.2f}·h{ch:.2f}·fill {cfill}) 하단 패딩 {_pad:.2f}in<0.25(pptx 실측) — "
                          f"어두운 카드는 하한 0.25in. 칩·본문을 위로 올려라. ERROR 0 전 '완료' 보고 금지.")
        elif ch < 2.5 and _btm > cy and not _dark24 and _pad < 0.10:
            errors.append(f"{_where} 카드(y{cy:.2f}·h{ch:.2f}) 내용이 하단 가장자리에 딱 붙음(하단 패딩 {_pad:.2f}in<0.10, pptx 실측) — "
                          f"칩·본문을 위로 올려 하단 패딩 0.18in 이상 확보하라. ERROR 0 전 '완료' 보고 금지.")
        elif ch < 2.5 and _btm > cy and not _dark24 and _pad < 0.18:
            warns.append(f"{_where} 카드(y{cy:.2f}·h{ch:.2f}) 하단 패딩 {_pad:.2f}in — 내용이 바닥에 가깝다. 0.18in 이상으로 띄워라(크롭 눈 확인).")

    # 26. 카드 내부 세로 성김(vertical_gap) —론 격상.
    #     y정렬만으로 재면 2열 카드에서 열끼리 인터리브돼 진짜 구멍을 놓침 →
    #     ① 카드 폭 60%+ 요소 = 풀폭(밴드·구분선): 모든 열의 커버리지에 산입, 열 클러스터링에서는 제외
    #     ② 나머지를 x-겹침 기준으로 열 클러스터링 ③ 열 안에서만 y커버리지 병합 후 내부 gap 실측.
    #     임계값): ERROR>0.60in / WARN>0.40in — 합격본에서 오탐 0, 반복 중간본에서 정탐 확인. 경계값(0.5~0.6)은 WARN으로 두어 차단하지 않는다. pptx 실측 경로 전용(js 추정은 함수 카드에서 오탐이 나 미구현).
    for (slide_name, cx, cy, cw, ch, cfill) in _cards_e:
        if ch < 1.8: continue
        _kids26 = [(x, y, w, h) for (sn, x, y, w, h, k, f) in _shapes_emu
                   if sn == slide_name
                   and not (abs(x-cx) < 0.02 and abs(y-cy) < 0.02 and abs(w-cw) < 0.02 and abs(h-ch) < 0.02)
                   and (cx-0.05 <= x < cx+cw-0.05 and cy-0.05 <= y < cy+ch)]
        if len(_kids26) < 2: continue
        _fullw = [(x, y, w, h) for (x, y, w, h) in _kids26 if w >= 0.6*cw]
        _rest = [(x, y, w, h) for (x, y, w, h) in _kids26 if w < 0.6*cw]
        _colsX = []   # [xmin, xmax, [(y1,y2),...]]
        for (x, y, w, h) in sorted(_rest):
            for _c in _colsX:
                if x < _c[1] + 0.05 and x + w > _c[0] - 0.05:
                    _c[0] = min(_c[0], x); _c[1] = max(_c[1], x + w); _c[2].append((y, y + h)); break
            else:
                _colsX.append([x, x + w, [(y, y + h)]])
        _where = os.path.basename(slide_name)
        for _c in _colsX:
            _iv = sorted(_c[2] + [(y, y + h) for (x, y, w, h) in _fullw])
            if len(_iv) < 2: continue
            _mrg = [list(_iv[0])]
            for (_a, _b) in _iv[1:]:
                if _a <= _mrg[-1][1] + 0.02: _mrg[-1][1] = max(_mrg[-1][1], _b)
                else: _mrg.append([_a, _b])
            _gaps26 = [(_mrg[_i+1][0] - _mrg[_i][1]) for _i in range(len(_mrg) - 1)]
            _mg = max(_gaps26) if _gaps26 else 0
            if _mg > 0.60:
                errors.append(f"#26 {_where} 카드(y{cy:.2f}·h{ch:.2f}) 내부 세로 gap {_mg:.2f}in>0.60 — 요소 사이 성김(pptx 실측, 열 클러스터 기준). "
                              f"요소를 세로 재분배하거나 내용을 채워 gap을 좁혀라. ERROR 0 전 '완료' 보고 금지.")
            elif _mg > 0.40:
                warns.append(f"#26 {_where} 카드(y{cy:.2f}·h{ch:.2f}) 내부 세로 gap {_mg:.2f}in — 성김 의심. 크롭 줌으로 눈 확인.")

    # 27. 네이티브 카드 우측 빈 세로기둥(gutter) —"행 요소가 카드 앞쪽 절반에서 끝남").
    #     #23은 통짜 PNG 전용이라 네이티브 카드용 좌표 검사로 이식).
    #     대상 집합: 카드 안 전 요소(sp·pic·graphicFrame) — 단 카드 면적 80%+ 덮는 배경성 요소 제외.
    #     rightmost=max(x+w) → 우측 빈 기둥 비율=(카드 우변−rightmost)/카드 폭. ERROR≥0.35(#23 기준선 공유) / WARN≥0.25.
    for (slide_name, cx, cy, cw, ch, cfill) in _cards_e:
        _kids27 = [(x, y, w, h) for (sn, x, y, w, h, k, f) in _shapes_emu
                   if sn == slide_name
                   and not (abs(x-cx) < 0.02 and abs(y-cy) < 0.02 and abs(w-cw) < 0.02 and abs(h-ch) < 0.02)
                   and (cx-0.05 <= x < cx+cw-0.05 and cy-0.05 <= y < cy+ch)
                   and (w * h < 0.8 * cw * ch)]
        if len(_kids27) < 2: continue
        _rm = max(x + w for (x, y, w, h) in _kids27)
        _gr = ((cx + cw) - _rm) / cw if cw else 0
        _where = os.path.basename(slide_name)
        if _gr >= 0.35:
            errors.append(f"#27 {_where} 카드(y{cy:.2f}·w{cw:.2f}) 우측 {_gr*100:.0f}% 빈 세로기둥(pptx 실측) — 행 요소가 카드 앞쪽에서 끝남. "
                          f"내용을 우측까지 채우거나 카드 폭을 줄여라. ERROR 0 전 '완료' 보고 금지.")
        elif _gr >= 0.25:
            warns.append(f"#27 {_where} 카드(y{cy:.2f}·w{cw:.2f}) 우측 {_gr*100:.0f}% 빔 — gutter 의심. 크롭 줌으로 눈 확인.")
else:             # ── js 소스 추정(pptx 없을 때만 — 함수로 그린 내용은 못 읽는 한계) ──
    for (cx, cy, cw, ch) in _cards:
        _btm = _content_bottom(js_nc, (cx, cy, cw, ch))
        _ratio = ((cy + ch) - _btm) / ch if ch else 0
        if _ratio > 0.45:
            errors.append(f"카드(y{cy:.2f}·h{ch:.2f}) 하단 {_ratio*100:.0f}% 빔 — 명백한 위 쏠림(참사 수준, js추정). "
                          f"본문으로 하단까지 채우거나 카드 높이를 줄여라. ERROR 0 전 '완료' 보고 금지.")
        elif _ratio > 0.30:
            warns.append(f"카드(y{cy:.2f}·h{ch:.2f}) 하단 {_ratio*100:.0f}% 빔 — 위 쏠림 의심(js추정, 함수로 그린 카드면 부정확할 수 있음 → pptx 인자 주거나 크롭 줌으로 눈 확인).")
        # #24(짝 게이트): 내용이 카드 바닥에 딱 붙음(하단 패딩 부족) —
        _pad = (cy + ch) - _btm
        if _btm > cy and _pad < 0.18:
            warns.append(f"카드(y{cy:.2f}·h{ch:.2f}) 하단 패딩 {_pad:.2f}in<0.18 — 내용이 바닥에 붙음(js추정). 칩·본문을 위로 올려라. pptx 실측으로 재확인.")

# 25. 텍스트 박스 '틀 > 텍스트' 금지 —"텍스트보다 텍스트를 감싸는 틀이 더 크다.
#     너는 상하 가운데 정렬로 생각하는데 박스가 커서 어긋난다. 지금까지 내가 계속 수정해 왔다 — 이제부턴 네가 맞춰서 줘라."
#     좌표 산술은 '박스' 기준인데 눈은 '글자'만 보므로, 박스에 여분 높이가 있으면 시각 중심이 어긋난다.
#     룰: 텍스트 박스 높이 h ≈ 줄수 × fontSize/72 × 1.25(×lineSpacing) + 0.1 이내로 텍스트에 딱 맞추고,
#         노드/카드 안 세로 배치는 '텍스트 실높이 그룹'을 산술 중앙 정렬한다.
#     (a) pptx 실측: 같은 슬라이드 안 텍스트 박스(rect+글자)끼리 겹침 = ERROR (좌표 사실 — 오탐 없음)
#     (b) js 추정: 박스가 텍스트 렌더 높이보다 0.55in+ 크면 ERROR, 0.35~0.55 WARN (배열은 breakLine 줄수 반영)
def _est_h25(seg, boxw):
    fs = _opt(seg, 'fontSize') or 12
    lsm = _opt(seg, 'lineSpacingMultiple') or 1.0
    cm = re.match(r'\s*("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')', seg)
    if cm:
        content = cm.group(1)[1:-1]; brk = content.count('\\n')
    else:
        am = re.match(r'\s*\[(.*?)\]\s*,\s*\{', seg, re.S)
        if not am: return None   # 변수·함수로 준 내용은 판단 불가 → 검사 제외(오탐 방지)
        content = ''.join(re.findall(r'text:\s*"((?:[^"\\]|\\.)*)"', am.group(1)))
        brk = len(re.findall(r'breakLine:\s*true', am.group(1)))
    if not content.strip(): return None
    units = sum(1.0 if ord(c) >= 0x1100 else 0.55 for c in content)
    em = fs / 72.0
    per = max(1.0, (boxw or 1.0) / (em * 1.02))
    lines = max(1, math.ceil(units / per), brk + 1)
    return lines * em * 1.25 * (lsm if lsm and lsm > 0 else 1.0)
_over25e, _over25w = [], []
for _chunk in re.split(r'\.addSlide\(\)', js_nc):
    for _m in re.finditer(r'\.addText\(', _chunk):
        _seg = _chunk[_m.end(): _m.end() + 900]
        _x, _y, _w, _h = _opt(_seg, 'x'), _opt(_seg, 'y'), _opt(_seg, 'w'), _opt(_seg, 'h')
        if None in (_x, _y, _w, _h): continue
        _est = _est_h25(_seg, _w)
        if _est is None: continue
        _slop = _h - _est
        if _slop > 0.55: _over25e.append((_y, _h, _est))
        elif _slop > 0.35: _over25w.append((_y, _h, _est))
if _over25e:
    _y0, _h0, _e0 = _over25e[0]
    errors.append(f"텍스트보다 큰 텍스트 박스 {len(_over25e)}건 (예: y{_y0:.2f} 박스 h{_h0:.2f} vs 텍스트 실높이 ≈{_e0:.2f}) — "
                  f"틀에 여분 높이가 있으면 좌표 중앙과 눈 중앙이 어긋난다. "
                  f"h를 줄수×fontSize/72×1.25(+0.1 이내)로 줄이고, 노드 안 세로 배치는 텍스트 실높이 그룹을 산술 중앙 정렬하라. ERROR 0 전 '완료' 금지.")
elif _over25w:
    _y0, _h0, _e0 = _over25w[0]
    warns.append(f"텍스트 박스가 텍스트보다 헐렁 {len(_over25w)}건 (예: y{_y0:.2f} h{_h0:.2f} vs ≈{_e0:.2f}) — "
                 f"박스를 텍스트 실높이에 맞춰라. 추정 오차 감안 WARN — 크롭 눈 확인.")
if pptx and os.path.exists(pptx):
    # (c) pptx 실측 오버사이즈 — js 추정이 못 읽는 헬퍼 함수(변수 텍스트)까지 최종 XML의 실제 글자·sz·박스로 잰다.
    #     valign top(기본)인데 박스가 텍스트보다 크면 = 아래 여분이 시각 중심을 무너뜨림 → ERROR.
    #     valign middle(anchor ctr)이면 기하 중심은 맞으니 큰 헐렁(2배+)만 WARN. autofit 박스는 제외.
    _ovl25, _fat25e, _fat25w = [], [], []
    def _est_xml25(_blk, _win):
        if '<a:normAutofit' in _blk: return None
        _lsm = re.search(r'<a:spcPct val="(\d+)"', _blk)
        _lsmv = int(_lsm.group(1)) / 100000.0 if _lsm else 1.0
        _paras = re.findall(r'<a:p>(.*?)</a:p>', _blk, re.S)
        if not _paras: return None
        _all_sz = [int(s) for s in re.findall(r'sz="(\d+)"', _blk)]
        _tot = 0.0
        for _p in _paras:
            _szs = [int(s) for s in re.findall(r'sz="(\d+)"', _p)] or _all_sz or [1200]
            _fs = max(_szs) / 100.0
            _em = _fs / 72.0
            _txt = ''.join(re.findall(r'<a:t>([^<]*)</a:t>', _p))
            _units = sum(1.0 if ord(c) >= 0x1100 else 0.55 for c in _txt)
            _per = max(1.0, _win / (_em * 1.02))
            _lines = max(1, math.ceil(_units / _per)) + _p.count('<a:br')
            _tot += _lines * _em * 1.25 * _lsmv
        return _tot
    with zipfile.ZipFile(pptx) as _z25:
        for _n25 in _z25.namelist():
            if not re.match(r'ppt/slides/slide\d+\.xml$', _n25): continue
            _sx25 = _z25.read(_n25).decode('utf-8', 'ignore'); _E25 = 914400.0
            _tb25 = []
            for _mm in re.finditer(r'<p:sp\b.*?</p:sp>', _sx25, re.S):
                _blk = _mm.group(0)
                if '<a:prstGeom prst="rect"' not in _blk: continue
                _txt25 = ''.join(re.findall(r'<a:t>([^<]*)</a:t>', _blk)).strip()
                if not _txt25: continue
                _o = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"', _blk)
                _e = re.search(r'<a:ext cx="(\d+)" cy="(\d+)"', _blk)
                if not (_o and _e): continue
                _bx, _by = int(_o.group(1))/_E25, int(_o.group(2))/_E25
                _bw, _bh = int(_e.group(1))/_E25, int(_e.group(2))/_E25
                _tb25.append((_bx, _by, _bw, _bh, _txt25[:14]))
                _estx = _est_xml25(_blk, _bw)
                if _estx:
                    _anch = re.search(r'<a:bodyPr[^>]*anchor="(\w+)"', _blk)
                    _mid = bool(_anch and _anch.group(1) == 'ctr')
                    _slop, _ratio = _bh - _estx, (_bh / _estx if _estx else 1.0)
                    if (not _mid) and _slop > 0.25 and _ratio > 1.8:
                        _fat25e.append((os.path.basename(_n25), _txt25[:14], _bh, _estx))
                    elif _mid and _slop > 0.55 and _ratio > 2.0:
                        _fat25w.append((os.path.basename(_n25), _txt25[:14], _bh, _estx))
            for _i in range(len(_tb25)):
                for _j in range(_i + 1, len(_tb25)):
                    x1, y1, w1, h1, t1 = _tb25[_i]; x2, y2, w2, h2, t2 = _tb25[_j]
                    _ox = min(x1 + w1, x2 + w2) - max(x1, x2)
                    _oy = min(y1 + h1, y2 + h2) - max(y1, y2)
                    if _ox > 0.25 * min(w1, w2) and _oy > 0.05:
                        _ovl25.append((os.path.basename(_n25), t1, t2, round(_oy, 2)))
    if _ovl25:
        _s25, _t1, _t2, _oy25 = _ovl25[0]
        errors.append(f"텍스트 박스끼리 겹침 {len(_ovl25)}건 (예: {_s25} '{_t1}'↔'{_t2}' 세로 {_oy25}in, pptx 실측) — "
                      f"틀이 텍스트보다 커서 이웃 박스를 침범(실제로 터진 지점). "
                      f"박스 높이를 텍스트 실높이로 줄이고 y를 재배분하라. ERROR 0 전 '완료' 금지.")
    if _fat25e:
        _s25, _t25, _h25, _e25f = _fat25e[0]
        errors.append(f"텍스트보다 큰 텍스트 박스(valign top) {len(_fat25e)}건 (예: {_s25} '{_t25}' 박스 h{_h25:.2f} vs 텍스트 ≈{_e25f:.2f}, pptx 실측) — "
                      f"아래 여분 높이가 시각 중심을 무너뜨린다. "
                      f"h=줄수×fontSize/72×1.25(+0.1 이내)로 줄이고, 노드 세로 배치는 텍스트 실높이 그룹을 산술 중앙 정렬. ERROR 0 전 '완료' 금지.")
    if _fat25w:
        _s25, _t25, _h25, _e25f = _fat25w[0]
        warns.append(f"헐렁한 중앙정렬 텍스트 박스 {len(_fat25w)}건 (예: {_s25} '{_t25}' h{_h25:.2f} vs ≈{_e25f:.2f}) — "
                     f"기하 중심은 맞지만 박스가 텍스트의 2배+. 편집·선택이 어수선해지니 텍스트 높이로 줄여라.")

# 28. 텍스트 수직 처짐 금지 —"텍스트가 텍스트박스보다 아래로 쳐진다.
#     박스 안 텍스트는 그 박스의 상하 센터에 위치해야 한다. 당연한 부분이다. 다신 이 실수 하지 마라."
#     실측(PowerPoint 실렌더 픽셀 계측, /tmp/vcenter_probe*): valign top은 기본 tIns 0.05"가 글자를
#     아래로 밀고 Pretendard 실제 줄피치(1.19em)가 h 추정(1.25em 이내 조임)을 넘겨 글자가 박스 하단을
#     이탈한다(topgap +0.062 / botgap −0.015). valign middle이면 기본 인셋이 상하 대칭(0.05/0.05)이라
#     완벽 대칭(+0.023/+0.023) — margin은 건드리지 않는다(좌우 인셋 0.1" 제거 시 가로 정렬 틀어짐).
#     룰: 모든 addText는 valign: "middle" (top·bottom·미지정 전부 ERROR).
#     (a) js 검사 — 괄호 균형 파싱으로 addText 옵션의 valign을 정확히 읽는다(900자 윈도 오탐 방지).
def _iter_addtext_opts(_code):
    _i = 0
    while True:
        _m = re.search(r'\.addText\(', _code[_i:])
        if not _m: return
        _st = _i + _m.end(); _d, _j, _ins, _esc, _q = 1, _st, False, False, ''
        while _d and _j < len(_code):
            _c = _code[_j]
            if _ins:
                if _esc: _esc = False
                elif _c == '\\': _esc = True
                elif _c == _q: _ins = False
            else:
                if _c in '"\'`': _ins, _q = True, _c
                elif _c == '(': _d += 1
                elif _c == ')': _d -= 1
            _j += 1
        yield _code[_st:_j-1]
        _i = _j
_sag28 = []
for _call28 in _iter_addtext_opts(js_nc):
    _vm = re.search(r'valign:\s*["\'](\w+)["\']', _call28)
    if not _vm or _vm.group(1) != 'middle':
        _yv = _opt(_call28, 'y')
        _sag28.append((_yv if _yv is not None else -1, _vm.group(1) if _vm else '미지정'))
if _sag28:
    _y28, _v28 = _sag28[0]
    errors.append(f"#28 valign middle 아닌 addText {len(_sag28)}건 (예: y{_y28:.2f} valign={_v28}) — "
                  f"valign top+기본 tIns 0.05\"는 글자를 박스 아래로 밀어 하단 이탈시킨다(PowerPoint 실렌더 실측). "
                  f"모든 addText에 valign: \"middle\" — 박스가 텍스트에 딱 맞으면(#25) middle=디자인 의도 그대로다. ERROR 0 전 '완료' 금지.")
if pptx and os.path.exists(pptx):
    # (b) pptx 실측 — 최종 XML에서 anchor="ctr" 강제 + tIns/bIns 비대칭 차단 + 글자 하단 이탈 추정.
    #     슬라이드번호 등 필드(<a:fld>)·빈 텍스트·autofit은 제외.
    _nc28, _asym28, _ovf28 = [], [], []
    def _ph_eff_anchor(_z, _slide, _phtag):
        # 플레이스홀더 유효 anchor 상속 해석): 슬라이드에 anchor가 없으면
        # 레이아웃 → 마스터 순으로 같은 ph(idx 우선, 없으면 type)를 찾아 anchor를 상속받는다.
        # 어디에도 없으면 OOXML 기본값 't'(top).
        _pt = re.search(r'type="(\w+)"', _phtag); _pi = re.search(r'idx="(\d+)"', _phtag)
        _chain = []
        try:
            _rels = _z.read(f'ppt/slides/_rels/{os.path.basename(_slide)}.rels').decode('utf-8', 'ignore')
            _lay = re.search(r'Target="\.\./(slideLayouts/[^"]+)"', _rels)
            if _lay:
                _chain.append('ppt/' + _lay.group(1))
                _lrels = _z.read(f'ppt/slideLayouts/_rels/{os.path.basename(_lay.group(1))}.rels').decode('utf-8', 'ignore')
                _mas = re.search(r'Target="\.\./(slideMasters/[^"]+)"', _lrels)
                if _mas: _chain.append('ppt/' + _mas.group(1))
        except KeyError:
            pass
        for _p in _chain:
            try: _px = _z.read(_p).decode('utf-8', 'ignore')
            except KeyError: continue
            for _sm in re.finditer(r'<p:sp\b.*?</p:sp>', _px, re.S):
                _sb = _sm.group(0)
                _sph = re.search(r'<p:ph\b[^>]*/?>', _sb)
                if not _sph: continue
                _st = re.search(r'type="(\w+)"', _sph.group(0)); _si = re.search(r'idx="(\d+)"', _sph.group(0))
                if _pi:
                    if not (_si and _si.group(1) == _pi.group(1)): continue
                elif not (_pt and _st and _pt.group(1) == _st.group(1)): continue
                _sbp = re.search(r'<a:bodyPr[^>]*>', _sb)
                _sa = re.search(r'anchor="(\w+)"', _sbp.group(0)) if _sbp else None
                if _sa: return _sa.group(1)
                break  # 이 단계에 anchor 없음 — 다음 단계(마스터)로 상속 계속
        return 't'
    with zipfile.ZipFile(pptx) as _z28:
        for _n28 in _z28.namelist():
            if not re.match(r'ppt/slides/slide\d+\.xml$', _n28): continue
            _sx28 = _z28.read(_n28).decode('utf-8', 'ignore')
            for _mm in re.finditer(r'<p:sp\b.*?</p:sp>', _sx28, re.S):
                _blk = _mm.group(0)
                # 예외는 명시로만): prstGeom 부재 = 기본 rect 텍스트박스이므로
                # 검사 대상 — anchor 미지정(기본 top)이면 그대로 ERROR(암묵 우회 경로 차단).
                # 플레이스홀더(<p:ph>)도 무조건 통과가 아니라 상속 최종 anchor를 해석한다:
                # slidenum·날짜 필드(페이지번호)·빈 ph만 통과, 실텍스트 ph는 유효 anchor ctr 강제.
                _txt28 = ''.join(re.findall(r'<a:t>([^<]*)</a:t>', _blk)).strip()
                _phm28 = re.search(r'<p:ph\b[^>]*/?>', _blk)
                if _phm28:
                    if '<a:fld' in _blk or not _txt28: continue
                    _bp0 = re.search(r'<a:bodyPr[^>]*>', _blk)
                    _a0 = re.search(r'anchor="(\w+)"', _bp0.group(0)) if _bp0 else None
                    _eff28 = _a0.group(1) if _a0 else _ph_eff_anchor(_z28, _n28, _phm28.group(0))
                    if _eff28 != 'ctr':
                        _nc28.append((os.path.basename(_n28), _txt28[:14], _eff28 + '(ph상속)'))
                    continue
                _g28 = re.search(r'<a:prstGeom prst="(\w+)"', _blk)
                if _g28 and _g28.group(1) != 'rect': continue  # 비직사각 도형 텍스트는 #28 대상 아님(8d 등 별도)
                if '<a:fld' in _blk or '<a:normAutofit' in _blk: continue
                if not _txt28: continue
                _bp = re.search(r'<a:bodyPr[^>]*>', _blk)
                _bps = _bp.group(0) if _bp else ''
                _anch = re.search(r'anchor="(\w+)"', _bps)
                if not (_anch and _anch.group(1) == 'ctr'):
                    _nc28.append((os.path.basename(_n28), _txt28[:14], _anch.group(1) if _anch else 't(기본)'))
                _ti = re.search(r'tIns="(-?\d+)"', _bps); _bi = re.search(r'bIns="(-?\d+)"', _bps)
                if (_ti is None) != (_bi is None) or (_ti and _bi and _ti.group(1) != _bi.group(1)):
                    _asym28.append((os.path.basename(_n28), _txt28[:14]))
                # 글자 하단 이탈: 실측 잉크 스팬 (줄수-1)×1.19em + 1.0em 이 박스보다 크면 넘침
                _e28 = re.search(r'<a:ext cx="(\d+)" cy="(\d+)"', _blk)
                if _e28:
                    _bw28, _bh28 = int(_e28.group(1))/914400.0, int(_e28.group(2))/914400.0
                    _szs = [int(s) for s in re.findall(r'sz="(\d+)"', _blk)] or [1200]
                    _fs28 = max(_szs)/100.0; _em28 = _fs28/72.0
                    _units = sum(1.0 if ord(c) >= 0x1100 else 0.55 for c in _txt28)
                    _per = max(1.0, _bw28/(_em28*1.02))
                    _ln28 = max(1, math.ceil(_units/_per)) + _blk.count('<a:br')
                    _ink28 = ((_ln28-1)*1.19 + 1.0) * _em28
                    if _ink28 > _bh28 + 0.06:
                        _ovf28.append((os.path.basename(_n28), _txt28[:14], _bh28, _ink28))
    if _nc28:
        _s28, _t28, _a28 = _nc28[0]
        errors.append(f"#28 anchor ctr 아닌 텍스트 {len(_nc28)}건 (예: {_s28} '{_t28}' anchor={_a28}, pptx 실측) — "
                      f"텍스트는 박스 상하 센터. valign: \"middle\"로 빌드하라. ERROR 0 전 '완료' 금지.")
    if _asym28:
        errors.append(f"#28 tIns/bIns 비대칭 텍스트 {len(_asym28)}건 (예: {_asym28[0][0]} '{_asym28[0][1]}') — "
                      f"상하 인셋이 다르면 middle이어도 센터가 어긋난다. margin은 스칼라 또는 상하 동일로.")
    if _ovf28:
        _s28, _t28, _h28, _k28 = _ovf28[0]
        warns.append(f"#28 글자가 박스 세로를 넘침 {len(_ovf28)}건 (예: {_s28} '{_t28}' 박스 h{_h28:.2f} < 잉크 ≈{_k28:.2f}, 실측 1.19em 피치) — "
                     f"middle이라 대칭 유지되나 이웃과 겹칠 수 있다. h를 잉크 이상으로.")

# 20. 카드 하단과 그 아래 '하단 띠' 사이 빈 공간(밀도 저하) —
#     "흰 박스와 하단 검은 박스 간격이 넓으면 밀도가 떨어진다. 박스를 키워 채워라."
#     하단부 폭넓은 띠(roundRect: y>5.2·w>8·h<0.9)의 상단과, 그 위 카드들의 최하단 사이 갭이 0.45in 초과면 WARN.
#     (첫 지적 → WARN. 재발 시 ERROR로 격상. false positive 위험 있어 하드차단은 보류 — feedback-to-code-gate)
_bands20 = []
for _m in re.finditer(r'\.addShape\(\s*([\w.]+)\s*,\s*\{', js_nc):
    if _shape_st(_m.group(1)) != 'roundRect': continue
    _seg = js_nc[_m.end() - 1: _m.end() + 360]
    bx, by, bw, bh = _opt(_seg, 'x'), _opt(_seg, 'y'), _opt(_seg, 'w'), _opt(_seg, 'h')
    if None in (bx, by, bw, bh): continue
    if by > 5.2 and bw > 8.0 and bh < 0.9:
        _bands20.append((bx, by, bw, bh))
for (bx, by, bw, bh) in _bands20:
    _above = [cy + ch for (cx, cy, cw, ch) in _cards if cy + ch <= by + 0.05 and not (cx + cw < bx or cx > bx + bw)]
    if not _above: continue
    _gap20 = by - max(_above)
    if _gap20 > 0.70:
        errors.append(f"카드 하단과 하단 띠 사이 {_gap20:.2f}in 떠서 밀도 저하(명백) — 흰 카드를 아래로 키워 갭을 0.25in 안으로 좁혀라 "
                      f"(간격이 넓으면 밀도가 떨어진다). 카드 키우면 내부는 세로 중앙 정렬로 위쏠림 방지. ERROR 0 전 '완료' 금지.")
    elif _gap20 > 0.45:
        warns.append(f"카드 하단과 하단 띠 사이 {_gap20:.2f}in 떠서 밀도 저하 — 흰 카드를 아래로 키워 갭을 0.25in 안으로 좁혀라 "
                     f"(간격이 넓으면 밀도가 떨어진다). 카드 키우면 내부는 세로 중앙 정렬로 위쏠림 방지.")

# 21. 좌우 라인 정렬 — 큰 박스(roundRect)들의 좌/우 끝이 슬라이드 공통 마진과 어긋나면 WARN
#"우측 라인 맞추라고 했을텐데? 좌측도 마찬가지"). 풀폭 박스(w>8)의 x·x+w로 마진을 잡고,
#     좌측 영역 박스는 좌측 마진에, 우측 영역 박스는 우측 마진에 ±0.05in 안으로 맞았는지 본다.
_allrr21 = []   # (x, y, w, h)
for _m in re.finditer(r'\.addShape\(\s*([\w.]+)\s*,\s*\{', js_nc):
    if _shape_st(_m.group(1)) != 'roundRect': continue
    _seg = js_nc[_m.end() - 1: _m.end() + 360]
    x21, y21, w21, h21 = _opt(_seg, 'x'), _opt(_seg, 'y'), _opt(_seg, 'w'), _opt(_seg, 'h')
    if None in (x21, y21, w21, h21) or w21 < 2.5: continue   # 칩·알약 등 작은 박스 제외
    _allrr21.append((x21, y21, w21, h21))
# 다른(더 큰) 박스 안에 완전 포함된 자식(서브박스·결론박스 등)은 정렬 대상에서 제외 — 최상위 박스만 검사
def _contained21(b, allb):
    x, y, w, h = b
    for (ox, oy, ow, oh) in allb:
        if (ox, oy, ow, oh) == b: continue
        if ow * oh > w * h and ox - 0.02 <= x and oy - 0.02 <= y and ox + ow + 0.02 >= x + w and oy + oh + 0.02 >= y + h:
            return True
    return False
_tops21 = [(x, w) for (x, y, w, h) in _allrr21 if not _contained21((x, y, w, h), _allrr21)]
_full21 = [(x, w) for (x, w) in _tops21 if w > 8.0]
if _full21 and len(_tops21) > len(_full21):
    _LM = min(x for x, w in _full21); _RM = max(x + w for x, w in _full21); _mid = (_LM + _RM) / 2
    _mis21 = []
    for (x, w) in _tops21:
        _cx = x + w / 2.0
        _isfull = (x <= _LM + 0.1 and x + w >= _RM - 0.1)   # 거의 전체 폭(풀폭 띠)
        if _isfull:                    # 풀폭 → 좌·우 둘 다 마진에
            if abs(x - _LM) > 0.05 or abs((x + w) - _RM) > 0.05: _mis21.append(('LR', x))
        elif _cx < _mid:               # 좌측 영역(중심 기준) → 좌측 마진만
            if abs(x - _LM) > 0.05: _mis21.append(('L', x))
        else:                          # 우측 영역(중심 기준) → 우측 마진만
            if abs((x + w) - _RM) > 0.05: _mis21.append(('R', x + w))
    if _mis21:
        warns.append(f"좌우 라인 정렬 깨짐 {len(_mis21)}건 — 박스 좌/우 끝이 공통 마진(L{_LM:.2f}·R{_RM:.2f})과 어긋남 "
                     f". 좌측 박스는 x={_LM:.2f}, 우측 박스는 x+w={_RM:.2f}에 맞춰라.")

# 22. 디자인 다양성 — '매번 같은 디자인 돌려먹기' 코드 검출 "매번 같은 디자인 돌려먹지 마, 메모리 말고 코드로 박아")
#     빌드마다 레이아웃 '지문'(시각요소 유형 + 카드 배치)을 .ppt-design-history.jsonl에 기록하고 직전 빌드와 비교.
#     ① 흰카드+글자만(시각화 0)이 2연속 = 명백한 돌려먹기 → ERROR 차단.  ② 레이아웃 지문이 직전과 완전 동일 → WARN.
#     ※ 이미지 내부 그래픽 종류(곡선/막대/타임라인…)까지는 코드가 못 가르니 그건 빌드 자문으로(과한 약속 X, 구조로 빈도↓).
import json as _json
_HIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".ppt-design-history.jsonl")
_base22 = os.path.basename(js_path)
_cards22 = [(x, w) for (x, w) in _tops21 if 1.2 < w < 8.0]           # 카드급 박스(풀폭 띠 제외)
_n_ext22 = len(_imgs)                                               # 배경·목업 제외 외부 그래픽(차트PNG·인포그래픽·사진)
_n_line22 = len(re.findall(r'ShapeType\.line', js_nc))
_n_ell22 = len(re.findall(r'ShapeType\.(ellipse|chord|arc|pie|donut)', js_nc))
if n_chart > 0 or n_chart_pptx > 0:   _vk22 = 'chart'   # 네이티브 차트는 pptx 실물로도 인식( TODO#5)
elif _n_ext22 > 0:                    _vk22 = 'image'               # 목업·인포그래픽·사진 박음
elif _n_line22 >= 4 or _n_ell22 >= 4: _vk22 = 'diagram'            # 노드·화살표 도식
else:                                 _vk22 = 'cards_text'          # 흰카드+글자만 = 가장 흔한 돌려먹기
_xs22 = tuple(sorted(round(x * 2) / 2 for x, w in _cards22))
_sig22 = f"{_vk22}|{len(_cards22)}c|{_xs22}"
_prev22 = []
if os.path.exists(_HIST):
    for _ln in open(_HIST, encoding='utf-8'):
        try: _prev22.append(_json.loads(_ln))
        except Exception: pass
_others22 = [r for r in _prev22 if r.get('file') != _base22]
if _others22:
    _last22 = _others22[-1]
    if _vk22 == 'cards_text' and _last22.get('vk') == 'cards_text':
        errors.append(f"🔁 텍스트 카드 레이아웃(시각화 0)이 직전 빌드({_last22.get('file')})와 연속 — "
                      f"'PPT 만들어'는 풀 시각화가 기본이고 '매번 같은 디자인 돌려먹기 금지'(). "
                      f"차트·도식(노드/화살표)·목업·인포그래픽·사진 중 직전과 다른 방식으로 시각화하라. ERROR 0 전 '완료' 금지.")
    elif _last22.get('sig') == _sig22:
        warns.append(f"🔁 직전 빌드({_last22.get('file')})와 같은 레이아웃 지문(유형 {_vk22}, 카드 {len(_cards22)}개 동일 배치) — "
                     f"'매번 같은 디자인 돌려먹지 마라'(). 판(레이아웃)·시각요소 종류를 직전과 다르게 가라. "
                     f"※ 이미지 내부 그래픽 종류(곡선/막대/타임라인 등)까지 같은지는 코드가 못 잡으니 스스로 점검.")
try:
    _keep22 = [r for r in _prev22 if r.get('file') != _base22]
    _keep22.append({'file': _base22, 'sig': _sig22, 'vk': _vk22, 'cards': len(_cards22), 'img': _n_ext22, 'chart': n_chart})
    _keep22 = _keep22[-60:]
    with open(_HIST, 'w', encoding='utf-8') as _f:
        for r in _keep22: _f.write(_json.dumps(r, ensure_ascii=False) + '\n')
except Exception: pass

# 23. 본문 삽입 이미지 내부 '한쪽 텅 빈 여백'(가로 gutter) —"꽉 채우랬지 크게 비우랬냐, 담부터 코드가 막아라"
#     Claude Design/HTML 통짜 PNG를 카드에 addImage하면 좌표 게이트(#19·#20)는 "카드가 이미지로 꽉 참"으로 통과하지만
#     이미지 '내부'가 텅 빈 건 좌표론 못 잡는다(HTML 통짜 우회의 구멍, v65 우측 3단계 카드 사고의 자리).
#     PIL로 이미지를 열어 흰(밝은)카드 영역을 밝기로 자동분할하고, 콘텐츠 없는 연속 세로기둥(가로 gutter)이
#     카드폭 35% 이상이면 ERROR. 다크 카드(터미널 등)는 배경이 어두워 자동 제외 → 오탐 0 지향.
#     기준선): 레퍼런스 우측패널 5~18% 통과 / v65 텅 빈 카드 60% 차단. 임계 35%는 그 사이 안전마진.
def _collect_img_full(txt):
    out = []
    for _m in re.finditer(r'\.addImage\(\s*\{', txt):
        seg = txt[_m.end() - 1: _m.end() + 280]
        pm = re.search(r'path:\s*([^,}\n]+)', seg)
        if not pm: continue
        praw = pm.group(1).strip()
        p = praw.strip('"\'') if praw[:1] in '"\'' else _strsym.get(praw, praw)
        if 'Background_' in p: continue
        out.append((p, _opt(seg, 'w')))
    return out
def _img_gutter(path):
    try:
        from PIL import Image
        import numpy as np
    except Exception:
        return None   # PIL/numpy 없으면 미검출(오탐보다 안전) — 이 경우만 눈 QA로
    if not os.path.exists(path): return None
    try:
        im = Image.open(path).convert("RGBA")
    except Exception:
        return None
    a = __import__('numpy').array(im).astype(int)
    import numpy as np
    r, g, b, al = a[:, :, 0], a[:, :, 1], a[:, :, 2], a[:, :, 3]
    H, W = r.shape
    if W < 200 or H < 120: return None   # 아이콘·작은 이미지 제외
    mn = np.minimum(np.minimum(r, g), b)
    opaque = al > 30
    ink = opaque & (mn < 235)
    bright = opaque & (mn >= 235)
    colbright = bright.mean(axis=0)
    iswhite = colbright > 0.35     # 흰 배경이 세로로 우세한 컬럼 = 흰카드
    segs = []; s = None
    for i, v in enumerate(list(iswhite) + [False]):
        if v and s is None: s = i
        elif (not v) and s is not None:
            if i - s > W * 0.15: segs.append((s, i))   # 카드폭 최소 15%
            s = None
    outg = []
    for cs, ce in segs:
        sub = ink[:, cs:ce]
        cols = np.array_split(sub, 40, axis=1)
        cf = [c.mean() * 100 for c in cols]
        mx = cur = 0
        for f in cf:
            cur = cur + 1 if f < 2 else 0
            if cur > mx: mx = cur
        outg.append((cs / W, ce / W, mx / 40 * 100))
    return outg
_gutter_skipped = False
for (_p, _w) in _collect_img_full(js_nc):
    if _w is None or _w < 3.0: continue    # 본문급 큰 이미지만(아이콘·로고 제외)
    _res = _img_gutter(_p)
    if _res is None:
        _gutter_skipped = True; continue
    for (_cs, _ce, _hg) in _res:
        if _hg >= 35:
            errors.append(f"본문 이미지({os.path.basename(_p)}) 안 흰카드(가로 {_cs*100:.0f}~{_ce*100:.0f}%)의 한쪽 "
                          f"{_hg:.0f}%가 콘텐츠 없이 텅 빈 세로기둥 — '꽉 채우랬지 크게 비우랬냐'(). "
                          f"레퍼런스 우측패널은 5~18%(분해바·표·게이지가 카드 끝까지 뻗음). 콘텐츠를 카드 폭 끝까지 채우고 "
                          f"큰 타이포로 여백 늘리기 금지. ERROR 0 전 '완료' 보고 금지.")
if _gutter_skipped:
    warns.append("본문 이미지 gutter 검사 일부 skip(PIL/numpy 미설치 또는 파일 없음) — 텅 빈 여백 있는지 PNG로 눈 확인.")

# ───────── 출력 ─────────
print(f"=== PPT Lint: {os.path.basename(js_path)}  (검사대상: {src}) ===")
if errors:
    print(f"❌ ERROR {len(errors)}건 — 통과 불가, 0으로 고쳐 다시 빌드:")
    for e in errors: print("   ✗", e)
if warns:
    print(f"⚠️  WARN {len(warns)}건 — PNG로 눈 확인:")
    for w in warns: print("   ·", w)
if not errors:
    print("✅ ERROR 0 — 코드 강제 룰 통과." + (" (WARN은 PNG로 확인 후 보고)" if warns else " 깔끔."))
else:
    print("→ ERROR 0 전엔 '완료' 보고 금지.")

# ── 코드가 못 잡는 것: 슬라이드 내부 논리 정합 (자문) ─────────────────
#   좌표·색·겹침은 코드가 본다. 그런데 "헤드라인이 지목한 항목이 차트·칩에 실제로 있는가"는
#   의미 판단이라 코드가 못 가른다. 데이터를 갈아끼울 때 헤드라인만 새로 쓰고 표·칩은
#   옛 배열을 두는 사고가 여기서 난다. 통과 전 눈으로 자문한다.
print("\n📋 코드가 못 잡는 자문 (통과 전 눈으로):")
print("   □ 헤드라인이 지목한 항목이 차트·표·칩에 전부 있는가? 순서까지 같은가?")
print("   □ 차트·칩·SO WHAT이 같은 데이터 집합을 말하는가? (한 곳만 고치고 나머지를 두지 않았나)")
print("   □ 수치가 서로 맞는가? (점유율·배수를 절대값에서 다시 계산해 대조)")
print("   □ 직전 슬라이드와 레이아웃 판이 다른가?")

sys.exit(1 if errors else 0)
