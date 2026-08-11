#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# writing_lint.py — 글쓰기·강의 스크립트 원칙 "코드 강제" 린터
# 강의 원고·뉴스레터·긴 글의 글쓰기 원칙을 검사한다.
#   ERROR 1건이라도 있으면 exit 1 → 이 글로 납품·발행 금지. 고쳐 통과시킬 것.
#   WARN 은 코드 근사(오탐 가능) → 눈으로 다듬기.
#   끝의 📋 체크리스트는 코드로 못 잡는 것(팩트·낭독 등) → 보고 전 반드시 사람이 자문.
# 사용:
#   일반 글: python3 writing_lint.py <글.txt>
#   표준입력: echo "글" | python3 writing_lint.py -
import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request


parser = argparse.ArgumentParser(description="페이퍼로지 글쓰기 린터")
parser.add_argument("source", nargs="?", default="-", help="검사할 UTF-8 텍스트 파일 또는 -")
args = parser.parse_args()

if args.source != '-':
    text = open(args.source, encoding='utf-8').read()
else:
    text = sys.stdin.read()

errors, warns = [], []

# ───────── ERROR (명확 금지) ─────────
if re.search(r'솔직(?:히|하게|한)', text): errors.append('"솔직히" 류 → 강조는 "정확히/상세히/짚어서"')
if re.search(r'(?:솔직|정직|정확)(?:하게|히)\s*(?:말|짚|얘기|보면|얘긴)', text): errors.append('"솔직하게/정직하게/정확하게 말하겠습니다·말하면·짚으면" 류 강조 도입부 → 쓸데없는 군말, 도입부 없이 바로 본론( "정확히 말하면도 하지마")')
if '—' in text: errors.append('줄표 em dash(—) → 콜론(:)·쉼표(,)·물결(~)')
if '–' in text: errors.append('줄표 en dash(–) → 물결(~)·콜론')
# 번역체 확정 패턴 (writing-no-translationese"글쓸 때 번역체 말투 쓰지 마")
if re.search(r'되어[지진질집졌]|되여지', text): errors.append('이중피동 "~되어지다" → "~되다" (번역체)')
if re.search(r'에 다름 아니', text): errors.append('"~에 다름 아니다" → "~일 뿐이다/바로 ~다" (일본어투 번역체)')
if re.search(r'지 않으면 안 [되된됩됐]', text): errors.append('"~지 않으면 안 된다" → "~해야 한다" (일본어투 번역체)')
if re.search(r'아무리 강조해도 지나치', text): errors.append('"아무리 강조해도 지나치지 않다" → 우리말로 바로 강조 (번역체)')
if '갈림길' in text: errors.append('"갈림길" 수사 금지 — 번역체로 읽힌다. 선택 상황은 입말로 풀 것("~하지 마세요, ~하세요")')

# ───────── WARN (코드 근사 → 눈 확인) ─────────
# 1. 대조말투 (writing-no-ai-antithesis)
anti = re.findall(r'(?:지 않습니다|이 아닙니다|가 아닙니다|지 않아요|는 게 아니라|것이 아니라|이 아니라|가 아니라)', text)
if len(anti) >= 3:
    warns.append(f'대조말투(antithesis) 남발 {len(anti)}곳 — "A 아니라 B"·"~하지 않습니다. ~합니다" 대구를 한 글에 3곳+ 반복하면 AI 티. 한두 번 강조는 OK, 남발만 종결 다양화로')
# 2. 과장 단정 (lecture-authoring §2: 동기부여로 살리되 사실 균형 한 줄)
exa = [w for w in ['모든', '전부', '무조건', '100%', '절대', '항상', '다 된다', '다 됩니다', '완벽하게'] if w in text]
if exa:
    warns.append(f'과장 단정 {exa} — 동기부여로 살리되 사실 균형 한 줄 붙였는지 (예: "모든 게 자동화되진 않지만 그렇게 덤비는 태도가 핵심")')
# 3. 긴 문장 (낭독 걸림 — "입으로 읽을 때 걸리면 안 된다")
sents = [s for s in re.split(r'(?<=[.?!])\s+', text) if s.strip()]
longs = [s for s in sents if len(s.replace(' ', '')) >= 90]
if longs:
    warns.append(f'긴 문장 {len(longs)}개(공백 제외 90자+) — 입으로 읽으면 숨이 참. 끊어 쓸 것. 예: "{longs[0][:32]}…"')
# 4. 같은 종결어미 3연속 (단조 — 종결 다양화)
def ending(s):
    s = s.strip().rstrip('.?! ')
    m = re.search(r'(니다|에요|예요|이에요|드라고요|거든요|네요|죠|아요|어요)$', s)
    return m.group(1) if m else None
ends = [ending(s) for s in sents]
run = maxrun = 1; prev = None
for e in ends:
    if e and e == prev: run += 1; maxrun = max(maxrun, run)
    else: run = 1
    prev = e
if maxrun >= 3:
    warns.append(f'같은 종결어미 {maxrun}연속 — 단조로움. 종결 다양화(~죠/~더라고요/의문형/명사 종결)')
# 5. 군더더기 부사
for w in ['근본적으로', '기본적으로', '사실은']:
    if w in text: warns.append(f'군더더기 부사 "{w}" — 빼는 게 깔끔'); break
# 6. 이모지 (강의 본문엔 절제 / 영상 스크립트 지시문은 예외)
emo = re.findall(r'[\U0001F000-\U0001FAFF☀-⛿✀-➿]', text)
if emo:
    warns.append(f'이모지 {" ".join(sorted(set(emo)))} — 강의 본문엔 절제 (영상 스크립트 지시문은 예외)')
# 8. 번역체 의심 (writing-no-translationese — 오탐 가능 패턴은 WARN, 확정 패턴은 위 ERROR)
trans = []
if re.search(r'가장[^.\n]{0,24}중 (?:의 )?하나', text): trans.append('"가장 ~한 것 중 하나"(one of the most) → "제일 ~한 게"')
if re.search(r'[을를] 가지고 있', text): trans.append('"~을 가지고 있다"(have 직역) → "~이 있다"')
if re.search(r'에 의해|에 의하여', text): trans.append('"~에 의해"(수동태) → 능동문으로')
if re.search(r'에 있어서?[\s,]', text): trans.append('"~에 있어(서)" → "~에서/~할 때" (단 "집에 있어서" 같은 진짜 있다 동사는 오탐)')
if re.search(r'할 필요가 있', text): trans.append('"~할 필요가 있다" → "~해야 한다/~하면 된다"')
if re.search(r'것이 가능하', text): trans.append('"~하는 것이 가능하다" → "~할 수 있다"')
if '에도 불구하고' in text: trans.append('"~에도 불구하고"(despite) → "~인데도/~지만"')
if '그녀' in text: trans.append('"그녀"(she 직역) → 이름·직함으로')
ndaehae = len(re.findall(r'에 대해|에 대한', text))
if ndaehae >= 4: trans.append(f'"에 대해/에 대한" {ndaehae}회(about 남용) → 조사로 풀기("~를", "~ 이야기")')
if re.search(r'(무엇이든|뭐든|누구든|어디든)[^.\n]{0,10}(?:힙니다|힌다|혀요|립니다|린다|려요|깁니다|긴다|겨요|어집니다|어진다|어져요)', text):
    trans.append('"무엇이든/뭐든 + 피동 단정"(anything can be read 직역) → 행위자 세워 능동으로 ("무엇이든 읽힙니다" X → "뭐든 던지면 읽습니다")')
if re.search(r'[가-힣]+(?:하는|기는|는) [건것](?:은)? 잘 (?:됩니다|돼요|되고요)', text):
    warns.append('부분 긍정 "~하는 건 잘 됩니다" — 은/는 대조 함축으로 "나머지는 안 된다"처럼 읽힘. 전부 되는 얘기면 "~도 그대로 됩니다/~까지 해줍니다"로')
if trans:
    warns.append('번역체 의심 — 한국어로 처음 쓴 문장처럼 다듬기 (writing-no-translationese): ' + ' / '.join(trans))

# ───────── 출력 ─────────
print("=== Writing / Lecture Lint ===")
if errors:
    print(f"❌ ERROR {len(errors)}건 — 고쳐 통과:")
    for e in errors: print("   ✗", e)
if warns:
    print(f"⚠️  WARN {len(warns)}건 — 눈으로 다듬기:")
    for w in warns: print("   ·", w)
if not errors:
    print("✅ ERROR 0 — 글쓰기 금지룰 통과.")
# 코드로 못 잡는 것 — 발행 전 사람이 반드시 자문 (항상 출력)
print("\n📋 코드로 못 잡음 — 발행 전 반드시 자문:")
print("   □ 팩트: 모든 사실·수치·기능·UI·명령어를 실제로 확인했는가? (추측·옛 기억 X) ← 1순위")
print("   □ 날조 0: 수치·약속·개인 서사는 출처가 확인된 것만 쓴다. 확실하지 않으면 톤을 낮추거나 뺀다")
print("   □ End Benefit: 한 줄마다 '읽는 사람이 결국 뭘 얻나·느끼나'까지 닿았는가? '우리가 ~한다'에서 멈춘 줄 0?")
print("   □ So what: 모든 줄에 '그래서?'를 끝까지 물어 결론까지 갔는가?")
print("   □ 요청 충실: 받은 브리프의 필수 키워드·금기어·타깃·목표를 다 반영했는가?")
print("   □ 낭독: 소리 내어 읽어 걸리는 문장이 없는가? (어색한 어순·중복·숨 참)")
print('   □ 번역체: 영어·일본어 직역 냄새("~중 하나"·"가지고 있다"·수동태·"에 대해" 남용) 없이 한국어로 처음부터 쓴 문장처럼 읽히는가?')
print("   □ 좋은 문장: 모아둔 문장·인용에서 맞는 구조(대구·역전·구체)가 있으면 빌리되 출처를 남겼는가? 없으면 억지로 끌어오지 않는다")
print("   □ 전문용어: 첫 등장 자리에 괄호로 한 줄 풀이를 붙였는가?")
print("   □ 경험: 쓰는 사람의 실제 경험을 1인칭으로 녹였는가?")
print("   □ 사생활 분리: 공개 콘텐츠에 가족·지인 이야기를 넣지 않았는가? 있으면 덜어낸다")
print("   □ 더 나은 방법: 처음 떠오른 방식에 안주하지 않고 더 좋은 설명·예시를 점검했는가?")
print("   □ 게으름: 상세히 써야 할 곳을 한 문단으로 압축하지 않았는가?")
sys.exit(1 if errors else 0)
