#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# brandlogy_lint.py — 카피 담당 카피 원칙 "코드 강제" 린터 (전 원칙판)
# 이 린터는 카피(슬로건·매니페스토·브랜드카피·PPT카피·메일·뉴스레터·피드백)를
# 쓸 때 지켜야 할 원칙을 빠짐없이 검사한다.
#   ERROR 1건이라도 있으면 exit 1 → 이 카피로 납품·빌드·회신 금지. 고쳐 통과시킬 것.
#   WARN 은 코드로 단정 못 함(오탐 가능) → 눈으로 다듬기.
# 사용: python3 brandlogy_lint.py <카피.txt>   |   echo "카피" | python3 brandlogy_lint.py -
import sys, re

# Windows cp949 콘솔에서 이모지/기호(❌⚠️✅ 등) print가 UnicodeEncodeError로 죽는 것 방지.
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

if len(sys.argv) > 1 and sys.argv[1] != '-':
    text = open(sys.argv[1], encoding='utf-8').read()
else:
    text = sys.stdin.read()

errors, warns = [], []

# ───────── ERROR (명확 금지·차단) ─────────
# 1. "솔직히" 류 (no-soljiki)
m = re.findall(r'솔직(?:히|하게|한|함)', text)
if m: errors.append(f'금지어 "솔직히" 류 {len(m)}곳 → 강조는 "정확히/상세히/짚어서"')
if re.search(r'(?:솔직|정직|정확)(?:하게|히)\s*(?:말|짚|얘기|보면|얘긴)', text): errors.append('"솔직하게/정직하게/정확하게 말하겠습니다·말하면" 류 강조 도입부 → 군말, 도입부 없이 바로 본론( "정확히 말하면도 하지마")')
# 2. 줄표
if '—' in text: errors.append('줄표 em dash(—) → 콜론(:)·쉼표(,)·물결(~)')
if '–' in text: errors.append('줄표 en dash(–) → 물결(~)·콜론')
# 3. 이모지 (카피 원칙) — Dingbats 대역엔 ✓·➡처럼 불릿/화살표로 흔히 쓰는 기호도 섞여 있어 제외한다.
_EMOJI_SAFE = set("✓✔✗✘➡➔→←↑↓·•‣◦")
emo = [e for e in re.findall(r'[\U0001F000-\U0001FAFF☀-⛿✀-➿⌀-⏿⬀-⯿]', text) if e not in _EMOJI_SAFE]
if emo: errors.append(f'이모지 {" ".join(sorted(set(emo)))} → 카피엔 이모지 금지')
# 4. 군더더기 부사 절대 금지 (§2)
for w in ['근본적으로', '기본적으로']:
    if w in text: errors.append(f'군더더기 부사 "{w}" → 삭제 (§2 절대 금지)')
# 4b. 번역체 확정 패턴 (writing-no-translationese"글쓸 때 번역체 말투 쓰지 마")
if re.search(r'되어[지진질집졌]|되여지', text): errors.append('이중피동 "~되어지다" → "~되다" (번역체)')
if re.search(r'에 다름 아니', text): errors.append('"~에 다름 아니다" → "~일 뿐이다/바로 ~다" (일본어투 번역체)')
if re.search(r'지 않으면 안 [되된됩됐]', text): errors.append('"~지 않으면 안 된다" → "~해야 한다" (일본어투 번역체)')
if re.search(r'아무리 강조해도 지나치', text): errors.append('"아무리 강조해도 지나치지 않다" → 우리말로 바로 강조 (번역체)')
if '갈림길' in text: errors.append('"갈림길" 수사 금지 — 번역체로 읽힌다. 선택 상황은 입말로 풀 것')
# COPYWRITING.md §1 "쓰지 말 것"이 명시적으로 금지어로 지정한 번역체 3종 — WARN이 아니라 ERROR다.
if re.search(r'가장[^.\n]{0,24}중 (?:의 )?하나', text): errors.append('"가장 ~한 것 중 하나"(one of the most) → "제일 ~한 게" (번역체, §1 금지)')
if re.search(r'[을를] 가지고 있', text): errors.append('"~을 가지고 있다"(have 직역) → "~이 있다" (번역체, §1 금지)')
if re.search(r'에 있어서?[\s,]', text): errors.append('"~에 있어(서)" → "~에서/~할 때" (번역체, §1 금지)')

# ───────── WARN (눈 확인) ─────────
# 5. 대조말투 antithesis (writing-no-ai-antithesis)
anti = re.findall(r'(?:지 않습니다|이 아닙니다|가 아닙니다|지 않아요|는 게 아니라|것이 아니라|이 아니라|가 아니라)', text)
if len(anti) >= 3:
    warns.append(f'대조말투(antithesis) 남발 {len(anti)}곳 — "A 아니라 B"·"~하지 않습니다. ~합니다" 대구를 한 글에 3곳+ 반복하면 AI 티. 한두 번 강조는 OK, 남발만 종결 다양화(~죠/~더라고요/의문형)로')
# 6. 군더더기 표현 (오탐 가능 → 경고, §2). 한 편의 카피에 여러 종류가 섞이면
# 전부 보여줘야지 하나 찾고 멈추면 나머지가 조용히 묻힌다.
_hedges = [w for w in ['사실은', '사실 ', '어떻게 보면', '말하자면', '다시 말해', '결국 말이죠'] if w in text]
if _hedges:
    warns.append(f'군더더기 표현 {[w.strip() for w in _hedges]} 의심 — 빼는 게 깔끔')
# 7. 메타 표현 (§16: "이 부분은 정말 중요한데" 류)
if re.search(r'이 (?:부분|점)(?:은|이)[^.]{0,15}(?:중요|핵심)', text) or '주목할' in text or '눈여겨' in text:
    warns.append('메타 표현(이 부분은 중요/주목할 만한) 의심 — 카피는 메타 없이 바로 본론 (§3-5)')
# 8. 사과·과한 겸양
_apologies = [w for w in ['죄송', '미안', '양해'] if w in text]
if _apologies:
    warns.append(f'사과 표현 {_apologies} — 사과문 카피가 아니면 빼라 (§2 사과 반복 금지)')
# 9. 카피 클리셰 (상투어 2개+면 경고)
cliche = [c for c in ['여정', '함께하', '당신의 꿈', '꿈을 향', '새로운 시작', '설렘', '특별한 순간', '가슴 뛰', '마음을 담', '빛나는'] if c in text]
if len(cliche) >= 2:
    warns.append(f'흔한 카피 클리셰 {cliche} — 메타포 없이 한 번에 이해되게, 흥행 감각으로 다시 (§3-5)')
# 10. 느낌표 남발 / 줄임표
if re.search(r'!{2,}', text) or text.count('!') >= 4:
    warns.append('느낌표 남발 — 절제')
if '…' in text or '...' in text:
    warns.append('줄임표(…) 의심 — 카피에선 절제, 문장으로 끊기')
# 11. 번역체 의심 (writing-no-translationese — 오탐 가능 패턴은 WARN, 확정 패턴은 위 ERROR)
trans = []
if re.search(r'에 의해|에 의하여', text): trans.append('"~에 의해"(수동태) → 능동문으로')
if re.search(r'할 필요가 있', text): trans.append('"~할 필요가 있다" → "~해야 한다"')
if re.search(r'것이 가능하', text): trans.append('"~하는 것이 가능하다" → "~할 수 있다"')
if '에도 불구하고' in text: trans.append('"~에도 불구하고"(despite) → "~인데도/~지만"')
if '그녀' in text: trans.append('"그녀"(she 직역) → 이름·직함으로')
# 짧은 카피는 "에 대해"가 3회면 이미 과하다고 보고, 긴 글(writing_lint)은 4회부터 본다 —
# 의도된 차이다(카피 vs 장문). 두 린터를 같이 고칠 땐 이 차이를 유지할 것.
ndaehae = len(re.findall(r'에 대해|에 대한', text))
if ndaehae >= 3: trans.append(f'"에 대해/에 대한" {ndaehae}회(about 남용) → 조사로 풀기')
if trans:
    warns.append('번역체 의심 — 한국어로 처음 쓴 문장처럼 (writing-no-translationese): ' + ' / '.join(trans))

print("=== Brandlogy Copy Lint ===")
if errors:
    print(f"❌ ERROR {len(errors)}건 — 이 카피로 납품/빌드/회신 금지:")
    for e in errors: print("   ✗", e)
if warns:
    print(f"⚠️  WARN {len(warns)}건 — 눈으로 다듬기:")
    for w in warns: print("   ·", w)
if not errors:
    print("✅ ERROR 0 — 카피 금지룰(줄표·이모지·솔직히·군더더기) 통과.")
else:
    print("→ ERROR 0 전엔 납품·빌드·회신 금지.")

# ============================================================================
# 카피 원칙 체크리스트 (매 카피 강제 자문, 항상 출력)
print("""
📋 카피 원칙 — 통과 전 전부 자문 (코드로 못 잡는 판단 영역):
   1. End Benefit  : 한 줄마다 '그래서 고객이 결국 뭘 얻나·느끼나'까지 닿았나?
                     '우리가 ~한다'(기능·과정·화자)에서 멈춘 줄이 0인가?
                     함정 : '당신~'을 목적절에만 얹고 주술은 화자면 그건 거울일 뿐이다.
                     고객이 결과의 주어가 돼야 진짜다.
   2. So what      : 모든 줄에 '그래서?'를 끝까지 물어 결론까지 갔나?
   3. 읽힘(낭독)   : 소리 내 읽어 걸리거나 안 읽히는 곳이 0인가?
   4. 검토=새 글   : 카피워싱·최소수정이 아니라 백지에서 새로 썼나?
   5. 모든 글      : 헤드·슬로건·매니페스토·설명·캡션까지 전부 같은 수준인가?
   6. 좋은 문장    : 모아둔 문장 아카이브에 맞는 구조(대구·역전·구체)가 있으면 빌리고
                     어디서 왔는지 근거를 남겼나? 확인은 필수, 차용은 더 좋을 때만.
                     결이 안 맞으면 억지로 끌어오지 않는다.
   7. 한 번에 이해 : 비유 없이 즉시 이해되나? 입말인가? 단위·주어를 밝혔나?
   7b. 번역체 0    : 영어·일본어 직역 냄새("~중 하나"·"가지고 있다"·수동태·"에 대해" 남용)
                     없이 한국어로 처음부터 쓴 문장처럼 읽히나?
   8. 브리프 충실  : 브리프의 필수 키워드·금기어·타깃·방향·목표를 다 반영했나?
                     두 축(브리프 자산 + 고객사 자체 서사)을 다 설득했나? 한 축만이면 카피워싱이다.
   9. 기준 소스    : 피드백을 받은 뒤라면 그 피드백이 브리프보다 우선이다.
  10. 날조 0       : 수치·약속·1인칭 서사는 출처가 확인된 것만. 확실하지 않으면 톤을 낮추거나 뺀다.
                     지어낸 1인칭 문장은 문법이 완벽해서 이 린터가 절대 못 잡는다.
  11. 클리셰 0     : 여정·함께하는·빛나는 류 상투어 없이 한 번에 꽂히나?
  12. 다른 눈      : 만든 사람이 자기 결과물을 통과시키는 구조는 반드시 한 번 뚫린다.
                     가능하면 만들지 않은 사람에게 1~11을 직접 보게 한다.
""")
sys.exit(1 if errors else 0)
