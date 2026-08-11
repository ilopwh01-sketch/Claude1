#!/usr/bin/env python3
"""검토 회신 게이트 — 칭찬한 클라이언트 원문을 수정본에서 몰래 갈아치우는 걸 막는다.

매니페스토 건에서 같은 사고가 하루에 세 번 났다.
회신 본문에 "○○도 좋습니다"라고 인용해 칭찬해놓고, 아래 수정본에서 그 문장을
손대거나 통째로 빼는 패턴. 받는 쪽에서는 "좋다는 거야 아니라는 거야"가 된다.

지적을 받으면 반사적으로 '고치는 방향'으로만 움직이는 버릇이 원인이라
의지가 아니라 코드로 막는다. 칭찬을 유지하려면 문장을 그대로 두고,
꼭 고쳐야 하면 칭찬을 빼거나 "다만 여기는 이렇게 바꿨습니다"를 명시해야 통과한다.

사용:
    python3 review_reply_lint.py <회신.txt>

수정본 구간은 본문 안의 `---` 구분선 사이로 본다(카피 검토 회신 표준 형식).
"""
import re
import sys

# 인용부호 계열 전부 — Gmail 웹·한글 문서를 거치면 곧은 따옴표가 스마트 인용부호로
# 자동 변환된다. `"` 하나만 보면 그 순간 게이트가 눈을 감는다).
_QO = '"\u201C\u201F\u2018\u201B\u300C\u300E'   # 여는: " " ‟ ' ‛ 「 『
_QC = '"\u201D\u2019\u300D\u300F'                 # 닫는: " " ' 」 』
PRAISE = re.compile(
    rf'[{_QO}]([^{_QC}]{{6,200}})[{_QC}]\s*(?:도|는|은|이|가)?\s*[^\n]{{0,40}}?'
    r'(좋습니다|좋았|훌륭|정확해요|정확합니다|살아있|압권|심장입니다|잘 쓰|탁월)'
)
_QUOTE_NORM = str.maketrans({c: '"' for c in _QO + _QC})


def split_revision(text):
    """`---` 구분선 사이를 수정본으로 본다. 없으면 (None, 이유)."""
    parts = text.split("\n---\n")
    if len(parts) < 3:
        return None, "수정본 구간(--- 사이)을 못 찾음"
    # 가장 긴 중간 블록을 수정본으로 (해설 중간의 --- 오탐 방지)
    return max(parts[1:-1], key=len), ""


def norm(s):
    return re.sub(r"\s+", "", s.translate(_QUOTE_NORM))


def check(path):
    text = open(path, encoding="utf-8").read()
    revision, why = split_revision(text)
    if revision is None:
        return [], [f"수정본 구간 미검출 — {why}. 검토 회신 형식이 아니면 이 게이트는 건너뛴다."]

    head = text.split("\n---\n")[0]          # 진단·칭찬부
    errors, warns = [], []
    seen = set()
    for m in PRAISE.finditer(head):
        quoted = m.group(1).strip()
        if norm(quoted) in seen:
            continue
        seen.add(norm(quoted))
        if norm(quoted) not in norm(revision):
            errors.append(
                f'칭찬한 원문이 수정본에 없다 → "{quoted[:60]}"\n'
                "      칭찬해놓고 갈아치우면 받는 쪽이 혼란스럽다. 원문 그대로 되돌리거나,\n"
                "      정말 고쳐야 하면 칭찬을 빼고 '여기는 이렇게 바꿨습니다'를 명시할 것."
            )
    if not seen:
        # fail-closed — '게이트가 못 읽음'과 '칭찬이 없음'은 구분이 안 되고, 둘 다 막아야 맞다.
        # 수정본 구간(---)이 있는 검토 회신인데 칭찬 인용이 0개면 통과시키지 않는다).
        errors.append(
            "칭찬 인용 0개 — 수정본 구간이 있는 검토 회신인데 잘한 곳을 하나도 인용하지 않았다.\n"
            "      ① 정말 칭찬이 없으면 먼저 잘한 곳을 짚어라(클라이언트 원고 검토의 기본).\n"
            "      ② 짚었는데 이 메시지가 뜨면 인용부호 형태가 게이트 밖이다 — _QO/_QC에 추가할 것."
        )
    return errors, warns


CHECKLIST = """
📋 통과 전 자문 (코드가 못 잡는 판단 영역)
   1. 지적받은 자리마다 "고칠 게 아니라 원문이 이미 맞았던 것 아닌가"를 물었나?
      → 오늘 사고 셋(에이전트 단수화·팀과 함께 누출·해설 덧붙이기)은 전부
        원문이 틀려서가 아니라 '고치는 손'에서 났다. 되돌리는 것도 조치다.
   2. 지적 하나를 고치면서 다른 자리를 새로 깨지 않았나? (고친 뒤 전체를 다시 읽었나)
   3. 이 회신이 상대가 물은 순서·언어로 답하고 있나? 내 언어(배치·구조·톤)로
      번역해서 말하고 있진 않나?
   4. 상대에게 넘기는 요청이 두 개 이상 흩어져 있지 않나? (묶어야 답이 온다)

   🚨 이 4개에 **뭐라고 답했는지 보고에 한 줄씩 적어라.**
      읽고 넘어가면 이건 게이트가 아니라 경고판일 뿐이다.
"""


def main():
    if len(sys.argv) < 2:
        print("사용: review_reply_lint.py <회신.txt>")
        sys.exit(2)
    errors, warns = check(sys.argv[1])
    print("=== Review Reply Lint ===")
    for w in warns:
        print(f"⚠️  WARN — {w}")
    for e in errors:
        print(f"🚫 ERROR — {e}")
    if errors:
        print(f"\n❌ ERROR {len(errors)}건 — 이 회신은 미완성이다. 발송·draft 금지.")
        sys.exit(1)
    print("✅ ERROR 0 — 칭찬한 원문이 수정본에 모두 살아있다.")
    print(CHECKLIST)


if __name__ == "__main__":
    main()
