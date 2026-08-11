#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mask_excel.py — 엑셀 개인정보 자동 마스킹 (AI에 넣기 전 1회 실행)

사용법:
    python3 mask_excel.py "고객명단.xlsx"
    python3 mask_excel.py --keep-mapping "고객명단.xlsx"  # 복원용 매핑표가 꼭 필요할 때만

결과:
    같은 폴더에  고객명단_마스킹_실행시각.xlsx  ← 이번 파일만 AI에 넣는다
    매핑표는 기본 생성하지 않는다. --keep-mapping일 때만 별도 금고에 저장한다

설계 원칙 (2026-08-01, 서린 적대 테스트로 3회 뚫린 뒤 재작성):
  · 컬럼명이 아니라 **값**을 보고 판정한다. 컬럼명은 보조 신호일 뿐이다.
    ("Product Name"을 사람 이름으로 오인해 분석을 망가뜨리지 않는다)
  · 검사를 **통과해야만** 파일을 저장한다. 실패하면 산출물이 디스크에 남지 않는다.
    (경고만 찍고 파일을 남기면 그건 게이트가 아니라 경고판이다)
  · 이름은 정규식으로 못 잡는다 → 치환표의 원본값을 결과 전 셀에서 역검색한다.
"""
import re
import sys
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path

try:
    import openpyxl
except ImportError:
    sys.exit("openpyxl이 필요합니다:  pip3 install openpyxl")

MAP_VAULT = Path.home() / "개인정보_매핑표_금고"

# ── 값 패턴 (컬럼 타입 판정 + 잔여 검사 양쪽에 쓴다) ──────────────
P_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]{2,}")
P_MOBILE = re.compile(r"01[016789][-\s.]?\d{3,4}[-\s.]?\d{4}")
P_LANDLINE = re.compile(r"(?<!\d)0(?:2|[3-6]\d)[-\s.]?\d{3,4}[-\s.]?\d{4}(?!\d)")
P_RRN = re.compile(r"(?<!\d)\d{6}[-\s]?[1-4]\d{6}(?!\d)")
P_CARD = re.compile(r"(?<!\d)\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}(?!\d)")
P_ACCOUNT = re.compile(r"(?<!\d)\d{2,6}-\d{2,6}-\d{2,8}(?!\d)")
P_KNAME = re.compile(r"^[가-힣]{2,4}$")
P_KFULLNAME = None   # SURNAME 정의 후 아래에서 채운다
P_DATEISH = re.compile(r"(19|20)\d{2}[-./년\s]?\s?\d{1,2}")

# 문장 속 제3자 이름 — 치환표 역검색으로는 원리적으로 못 잡는 자리.
# "김철수 고객님", "이영희씨", "최민수 과장"은 잡고 "다음 고객님께"는 안 잡아야 한다.
# → 호칭만 보면 오탐이 난다. 반드시 '성씨로 시작'을 함께 요구한다.
SURNAME = ("김이박최정강조윤장임한오서신권황안송류전홍고문양손배백허유남심노정하곽성차주우구"
           "신임나전민유진지엄채원천방공강현함변염양변여추노도소신석선설마길주연방위표명기"
           "반왕금옥육인맹제모장남탁국여진어은편구용")
HONORIFIC = ("씨", "님", "군", "양", "고객", "회원", "대표", "사장", "부사장", "전무", "상무",
             "이사", "본부장", "실장", "팀장", "부장", "차장", "과장", "대리", "주임", "사원",
             "선생", "교수", "박사", "원장", "소장", "국장", "위원", "총무", "간사", "기사")
P_NAME_TITLE = re.compile(
    r"[" + SURNAME + r"][가-힣]{1,2}\s?(?:" + "|".join(HONORIFIC) + r")(?:님|장|급)?"
)
# 이름 없이 쓰이는 일반 호칭. '고객님'의 '고'가 성씨라 김·고·유 등에서 오탐이 난다.
GENERIC_TITLE = {
    "고객님", "고객", "회원님", "회원", "손님", "선생님", "기사님", "사장님", "대표님",
    "팀장님", "과장님", "부장님", "차장님", "대리님", "실장님", "이사님", "원장님",
    "교수님", "박사님", "주임님", "사원님", "담당자님", "관리자님", "본부장님", "소장님",
    "위원님", "국장님", "전무님", "상무님", "부사장님", "총무님", "간사님",
}


def name_leaks(text):
    """이름+호칭 조합만 골라낸다. 이름 없는 일반 호칭은 제외."""
    return [m.group(0) for m in P_NAME_TITLE.finditer(text)
            if m.group(0).replace(" ", "") not in GENERIC_TITLE]


# ── 의심 신호 (차단은 안 하지만 반드시 화면에 띄운다) ────────────
# 호칭 없이 적힌 이름("김철수 재문의")·문장 속 영문 성명("Contact John Smith").
# 정규식으로 확정할 수 없어 차단하면 오탐이 폭증한다. 대신 눈으로 보게 만든다.
P_SUSPECT_KNAME = re.compile(r"(?<![가-힣])[" + SURNAME + r"][가-힣]{1,2}(?![가-힣])")
P_SUSPECT_ENNAME = re.compile(r"\b[A-Z][a-z]{1,15}\s[A-Z][a-z]{1,15}\b")
KNAME_STOP = {"그리고", "하지만", "그래서", "다음", "이번", "지난", "오늘", "내일", "어제",
              "신규", "기존", "담당", "확인", "완료", "진행", "요청", "문의", "안내", "전달",
              "관련", "추가", "변경", "취소", "예정", "가능", "불가", "필요", "검토", "보류"}
# 행정구역·동사형 어미로 끝나면 사람 이름이 아니다 ('강남구'·'안내함'·'성남시' 오탐 차단)
KNAME_TAIL_STOP = ("구", "시", "군", "동", "읍", "면", "리", "로", "길", "가", "층",
                   "함", "됨", "중", "말", "점", "실", "과", "부", "팀", "건", "안", "물")
ENNAME_STOP = {"Product Name", "New York", "Customer Service", "Sales Team", "Order Date",
               "Total Amount", "United States", "Hong Kong"}


P_OUR_ID = re.compile(r"^[가-힣A-Za-z]{1,10}\d{4}$")   # 우리가 만든 치환 ID


def suspects(text):
    """확정은 못 하지만 사람이 봐야 하는 것들"""
    if P_OUR_ID.match(text.strip()):
        return []                                       # 치환 ID는 우리 산출물이다
    found = []
    for m in P_SUSPECT_KNAME.finditer(text):
        w = m.group(0)
        # 한국 이름은 성+2자(3글자)가 압도적. 2자만 보면 오탐이 경고를 덮어버린다.
        if len(w) >= 3 and w not in KNAME_STOP and not w.endswith(KNAME_TAIL_STOP):
            found.append(w)
    for m in P_SUSPECT_ENNAME.finditer(text):
        if m.group(0) not in ENNAME_STOP:
            found.append(m.group(0))
    return found
# 한국 성명 — 성씨로 시작하는 2~4자. '머그'·'노트'를 이름으로 오인하지 않는다
P_KFULLNAME = re.compile(r"^[" + SURNAME + r"][가-힣]{0,3}$")
# 한자 성명 — 실무 명단에 "성함(한자)" 컬럼이 흔하다
P_CJKNAME = re.compile(r"^[\u4e00-\u9fff]{2,4}$")
# 영문 성명 — "Pen"·"Mug" 같은 단어 하나는 이름으로 보지 않는다
P_ENNAME = re.compile(r"^[A-Z][a-z]{1,15}(?:\s[A-Z]\.?)?\s[A-Z][a-z]{1,15}$")
# 행정구역 경계 — 공백이 없어도 시·군·구까지만 남기고 자른다
P_ADDR_CUT = re.compile(
    r"^\s*([가-힣]+(?:특별자치시|특별자치도|특별시|광역시|[가-힣]?도)|[가-힣]{2,4}시)"
    r"\s*([가-힣]+(?:시|군|구))?"
)

LEAK = [
    ("이메일", P_EMAIL),
    ("휴대전화", P_MOBILE),
    ("유선전화", P_LANDLINE),
    ("주민등록번호", P_RRN),
    ("카드번호", P_CARD),
    ("계좌번호", P_ACCOUNT),
]

# ── 컬럼명 보조 신호 (토큰 단위 완전일치. 부분 문자열 매칭 금지) ──
TOK_NAME = {"이름", "성명", "성함", "고객명", "회원명", "담당자", "수신자", "name", "성"}
PHONE_HEADERS = {"전화", "전화번호", "휴대전화", "휴대전화번호", "휴대폰", "핸드폰", "연락처",
                 "phone", "phonenumber", "mobile", "mobilenumber", "tel", "telephone"}
EMAIL_HEADERS = {"이메일", "메일", "전자우편", "email", "emailaddress", "mail"}
NONPERSON_NAME_HEADERS = {
    "productname", "itemname", "servicename", "filename", "projectname", "companyname", "brandname",
    "상품명", "제품명", "품목명", "서비스명", "파일명", "프로젝트명", "회사명", "브랜드명",
}
TOK_ID = {"고객번호", "회원번호", "사번", "아이디", "id", "userid", "customerid", "고객id"}
TOK_BIRTH = {"생년월일", "생일", "출생", "출생일", "birth", "birthday", "dob"}
TOK_ADDR = {"주소", "거주지", "자택주소", "address", "addr", "소재지"}
TOK_MONEY = {"금액", "매출", "소득", "연봉", "결제금액", "구매금액", "amount", "salary", "income"}
TOK_DROP = {"주민등록번호", "주민번호", "여권번호", "운전면허", "면허번호", "계좌번호",
            "카드번호", "cvc", "비밀번호", "password", "ssn"}


def norm(s):
    if s is None:
        return ""
    return unicodedata.normalize("NFKC", str(s)).strip().lower()


def tokens(header):
    """컬럼명을 토큰으로 쪼갠다. 'Product Name' -> {'product','name','productname'}"""
    h = norm(header)
    parts = set(re.split(r"[\s_\-/()\[\]]+", h)) - {""}
    parts.add(re.sub(r"[\s_\-/()\[\]]", "", h))
    return parts


def sniff(header, values):
    """값을 보고 컬럼 타입을 정한다. 컬럼명은 이름/생일/주소/금액에서만 보조로 쓴다."""
    tk = tokens(header)
    compact_header = re.sub(r"[\s_\-/()\[\]]", "", norm(header))
    vals = [str(v).strip() for v in values if v is not None and str(v).strip() != ""]

    if tk & TOK_DROP:
        return "drop"
    if not vals:
        return "keep"

    # 엑셀이 010의 앞 0을 없애 숫자 1012345678로 저장해도 컬럼명으로 막는다.
    if compact_header in PHONE_HEADERS or compact_header in EMAIL_HEADERS:
        return "id"

    sample = vals[:200]
    n = len(sample)

    def ratio(pat):
        return sum(1 for v in sample if pat.search(v)) / n

    def only(pat):
        """값이 '오직 그것 하나'인 비율. 문장 속에 섞인 경우는 세지 않는다.
        (자유 텍스트 컬럼을 통째로 ID 치환해 없애버리는 사고 방지)"""
        return sum(1 for v in sample if pat.fullmatch(v)) / n

    # 값으로 확정되는 것들 — 컬럼명이 뭐든 상관없다
    if only(P_RRN) >= 0.5 or only(P_CARD) >= 0.5:
        return "drop"
    if only(P_EMAIL) >= 0.5:
        return "id"
    if only(P_MOBILE) >= 0.5 or only(P_LANDLINE) >= 0.5:
        return "id"
    if (tk & TOK_DROP or "계좌" in norm(header)) and ratio(P_ACCOUNT) >= 0.5:
        return "drop"

    # 컬럼명 신호 + 값 형태가 둘 다 맞을 때만 (Product Name 오탐 차단)
    if tk & TOK_NAME:
        if compact_header in NONPERSON_NAME_HEADERS:
            return "keep"
        # '머그'·'노트'도 한글 2~4자라 그것만으로는 이름과 못 가른다.
        # → 한국 성씨로 시작하는 2~4자, 또는 영문 성명 형태. 그리고 컬럼 다수결 8할.
        looks_name = sum(1 for v in sample
                 if P_KFULLNAME.match(v) or P_ENNAME.match(v) or P_CJKNAME.match(v)) / n
        if looks_name >= 0.8:
            return "id"
        return "keep_warn"          # 이름 계열이지만 값이 사람 이름 형태가 아님

    if tk & TOK_ID:
        if any(len(v) > 30 for v in sample):
            return "keep"
        return "id"

    if tk & TOK_BIRTH and ratio(P_DATEISH) >= 0.4:
        return "birth"
    if tk & TOK_ADDR:
        return "addr"
    if tk & TOK_MONEY:
        numeric = sum(1 for v in sample if re.fullmatch(r"[\d,.\s원₩-]+", v)) / n
        if numeric >= 0.6:
            return "money"

    return "keep"


def age_band(v):
    if v is None or str(v).strip() == "":
        return ""
    m = re.search(r"(19|20)\d{2}", str(v))
    if not m:
        return "확인불가"
    age = datetime.now().year - int(m.group(0))
    if age < 20:
        return "10대 이하"
    if age >= 70:
        return "70대 이상"
    return f"{(age // 10) * 10}대"


def addr_cut(v):
    """시·도 + 시·군·구까지만 남긴다. 공백이 없는 주소도 행정구역 경계로 자른다."""
    if v is None or str(v).strip() == "":
        return ""
    s = str(v).strip()
    m = P_ADDR_CUT.match(s)
    if m:
        return " ".join(p for p in m.groups() if p)
    parts = s.split()
    if len(parts) >= 2:
        return " ".join(parts[:2])
    # 행정구역으로도, 공백으로도 못 자르는 주소는 통째로 내보내지 않는다
    return "주소미분류"


def money_band(v):
    if v is None or str(v).strip() == "":
        return ""
    try:
        n = float(re.sub(r"[^\d.-]", "", str(v)))
    except ValueError:
        return "확인불가"
    if n < 0:
        return "음수"
    for cap in (1_000_000, 3_000_000, 5_000_000, 10_000_000, 50_000_000):
        if n < cap:
            return f"~{cap // 10_000}만원"
    return "5000만원 이상"


def main():
    args = sys.argv[1:]
    keep_mapping = "--keep-mapping" in args
    args = [a for a in args if a != "--keep-mapping"]
    if len(args) != 1:
        sys.exit(__doc__)
    src = Path(args[0]).expanduser()
    if not src.exists():
        sys.exit(f"파일이 없습니다: {src}")

    wb = openpyxl.load_workbook(src, data_only=True)
    out = openpyxl.Workbook()
    out.remove(out.active)
    mapping = None
    if keep_mapping:
        mapping = openpyxl.Workbook()
        mapping.remove(mapping.active)

    report, warns = [], []
    all_originals = set()

    for ws in wb.worksheets:
        rows = list(ws.iter_rows(values_only=True))
        # 1행이 시트 제목이고 빈 행 뒤에 진짜 헤더가 오는 실무 양식이 흔하다.
        # 다만 '채워진 셀이 가장 많은 행'만 보면, 헤더 한 칸이 비었을 때
        # 첫 데이터 행이 헤더로 올라가 개인정보가 컬럼명이 된다(2026-08-01 실측).
        #   - 이메일·전화·주민번호가 있는 행은 헤더가 아니라 데이터다 → 후보 제외
        #   - 채워진 칸 수가 비슷하면(2칸 이내) 위쪽 행이 헤더다
        def _is_data_row(_r):
            for _c in _r:
                if _c is None:
                    continue
                _s = str(_c)
                if (P_EMAIL.search(_s) or P_MOBILE.search(_s)
                        or P_LANDLINE.search(_s) or P_RRN.search(_s)):
                    return True
            return False

        cands = []
        for _i, _r in enumerate(rows[:10]):
            if _is_data_row(_r):
                continue
            _f = sum(1 for _c in _r if _c is not None and str(_c).strip() != "")
            if _f:
                cands.append((_i, _f))
        hdr_i = 0
        if cands:
            _best = max(_f for _, _f in cands)
            hdr_i = next(_i for _i, _f in cands if _f >= _best - 2)
        if hdr_i:
            rows = rows[hdr_i:]
        if not rows:
            continue
        header = list(rows[0])
        body = rows[1:]

        kinds = []
        for i, h in enumerate(header):
            col_vals = [r[i] if i < len(r) else None for r in body]
            k = sniff(h, col_vals)
            if k == "keep_warn":
                warns.append(f"{ws.title}·{h}: 이름 계열 컬럼명이지만 값이 사람 이름 형태가 아니라 그대로 뒀습니다")
                k = "keep"
            kinds.append(k)

        keep_idx = [i for i, k in enumerate(kinds) if k != "drop"]
        dropped = [header[i] for i, k in enumerate(kinds) if k == "drop"]

        ows = out.create_sheet(ws.title[:31])
        ows.append([header[i] for i in keep_idx])

        id_map, counter, map_rows, id_count = {}, {}, [], 0

        for r in body:
            if all(c is None or str(c).strip() == "" for c in r):
                continue
            newrow = []
            for i in keep_idx:
                v = r[i] if i < len(r) else None
                k = kinds[i]
                if k == "id":
                    if v is None or str(v).strip() == "":
                        newrow.append("")
                        continue
                    raw = str(v).strip()
                    col = re.sub(r"[^\w가-힣]", "", norm(header[i])) or f"col{i}"
                    key = (col, raw)
                    if key not in id_map:
                        counter[col] = counter.get(col, 0) + 1
                        id_map[key] = f"{col.upper()[:6]}{counter[col]:04d}"
                        id_count += 1
                        if keep_mapping:
                            map_rows.append([ws.title, header[i], raw, id_map[key]])
                        if len(raw) >= 2:
                            all_originals.add(raw)
                    newrow.append(id_map[key])
                elif k == "birth":
                    newrow.append(age_band(v))
                elif k == "addr":
                    newrow.append(addr_cut(v))
                elif k == "money":
                    newrow.append(money_band(v))
                else:
                    newrow.append("" if v is None else v)
            ows.append(newrow)

        if keep_mapping and map_rows:
            mws = mapping.create_sheet(ws.title[:31])
            mws.append(["시트", "원본컬럼", "원본값", "치환ID"])
            for mr in map_rows:
                mws.append(mr)

        report.append((ws.title, dropped, id_count, max(0, len(body))))

    # ── 검사 (저장 전에 한다. 실패하면 파일이 안 생긴다) ────────────
    leaks = Counter()
    samples = {}
    suspect_hits = {}

    def flag(label, text):
        leaks[label] += 1
        samples.setdefault(label, str(text)[:50])

    for ws in out.worksheets:
        for ri, row in enumerate(ws.iter_rows(values_only=True)):
            if ri == 0:
                # 헤더는 데이터가 아니라 경보에서 뺀다(피로 방지). 다만 컬럼명 자리에
                # 이메일·전화·주민번호가 있으면 그건 헤더가 아니라 새어나온 데이터다.
                for c in row:
                    if c is None:
                        continue
                    s = str(c)
                    for label, pat in LEAK:
                        if pat.search(s):
                            flag(f"{label}(컬럼명 자리)", s)
                continue
            for c in row:
                if c is None:
                    continue
                s = str(c)
                for label, pat in LEAK:
                    if pat.search(s):
                        flag(label, s)
                if name_leaks(s):
                    flag("문장 속 사람 이름", s)
                for sus in suspects(s):
                    suspect_hits.setdefault(sus, str(c)[:45])
                # 치환한 원본값이 다른 칸(비고·메모 등)에 그대로 살아 있는가
                for orig in all_originals:
                    if orig in s and s != orig:
                        flag("치환한 원본값 재등장", s)
                        break

    print(f"\n원본:   {src.name}")
    for title, dropped, n_id, n_row in report:
        print(f"[{title}] {n_row}행", end="")
        if dropped:
            print(f" · 삭제 컬럼: {', '.join(str(d) for d in dropped)}", end="")
        print(f" · ID 치환 {n_id}건")

    if leaks:
        print("\n🚨 잔여 개인정보 발견 — 마스킹 파일을 만들지 않고 중단했습니다")
        for label, cnt in leaks.items():
            print(f"  {label} {cnt}건   예) {samples[label]}")
        print("\n  → 해당 칸(비고·메모 등)에서 개인정보를 지운 뒤 다시 실행하세요.")
        print("  → 산출물이 디스크에 남지 않았으므로 실수로 올라갈 위험은 없습니다.")
        sys.exit(1)

    # ── 통과한 경우에만 저장 ────────────────────────────────────
    # 이전 정상본을 지우지 않는다. 실행 시각을 붙여 이번 결과를 구분한다.
    # 같은 초에 여러 번 실행해도 덮어쓰지 않도록 충돌 시 번호를 붙인다.
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    suffix = stamp
    collision = 1
    masked_path = src.with_name(f"{src.stem}_마스킹_{suffix}.xlsx")
    map_candidate = MAP_VAULT / f"{src.stem}_매핑표_{suffix}.xlsx"
    while masked_path.exists() or (keep_mapping and map_candidate.exists()):
        collision += 1
        suffix = f"{stamp}-{collision}"
        masked_path = src.with_name(f"{src.stem}_마스킹_{suffix}.xlsx")
        map_candidate = MAP_VAULT / f"{src.stem}_매핑표_{suffix}.xlsx"

    out.save(masked_path)
    map_path = None
    if keep_mapping and mapping.sheetnames:
        MAP_VAULT.mkdir(mode=0o700, exist_ok=True)
        try:
            MAP_VAULT.chmod(0o700)
        except OSError:
            pass
        map_path = map_candidate
        mapping.save(map_path)
        try:
            map_path.chmod(0o600)
        except OSError:
            pass

    print("\n✅ 패턴 검사 통과 — 이메일·휴대전화·유선전화·주민번호·카드번호·계좌번호·치환한 원본값 0건")
    print(f"\n마스킹: {masked_path}")
    print("        ↑ 이 파일만 AI에 넣습니다")
    if map_path:
        print(f"매핑표: {map_path}")
        print("        ↑ 원본 폴더 밖에 따로 저장했습니다. AI에 넣지 마세요")
        print("🔐 매핑표에는 원본 개인정보가 평문으로 들어 있습니다. 복원이 끝나면 삭제하세요.")
    elif any(n_id for _, _, n_id, _ in report):
        print("\n🔒 매핑표는 저장하지 않았습니다 (기본값)")
        print("   원본 복원용 연결표가 꼭 필요할 때만 --keep-mapping으로 다시 실행하세요.")
    if warns:
        print("\n※ 참고")
        for w in warns:
            print(f"  · {w}")

    if suspect_hits:
        print("\n⚠️ 사람 이름일 수 있는 문자열이 남아 있습니다 — 눈으로 확인하세요")
        for w, ctx in list(suspect_hits.items())[:12]:
            print(f"   · \"{w}\"   ← {ctx}")
        if len(suspect_hits) > 12:
            print(f"   · … 외 {len(suspect_hits) - 12}건")
        print("   (확정할 수 없어 차단하지 않았습니다. 사람 이름이면 지우고 다시 실행하세요)")

    print("\n🚫 이 검사가 못 잡는 것 — 반드시 읽으세요")
    print("   · 호칭 없이 적힌 이름 (예: \"김철수 재문의\") — 위 ⚠️ 목록으로만 안내됩니다")
    print("   · 지역＋연령＋직책 조합으로 한 사람이 특정되는 경우")
    print("   · 자유 텍스트(상담메모·비고) 안의 회사명·사건명 등 간접 식별자")
    print("   → 통과 = '패턴이 안 걸렸다'이지 '개인정보가 없다'가 아닙니다.")
    print("      메모·비고 칸은 한 번 눈으로 훑고 AI에 넣으세요.")


if __name__ == "__main__":
    main()
