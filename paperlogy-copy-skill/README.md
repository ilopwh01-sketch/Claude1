# 페이퍼로지 카피라이팅 스킬

슬로건·매니페스토·브랜드 카피를 쓰는 순서와 원칙, 그리고 어긴 것을 잡아내는 검사 코드 묶음이다.

## 설치

Claude Code 스킬 폴더에 통째로 넣는다.

```bash
unzip paperlogy-copy-skill.zip -d ~/.claude/skills/
```

프로젝트 안에서만 쓰려면 `<프로젝트>/.claude/skills/` 아래에 둔다.
필요한 것은 Python 3뿐이다. 추가 패키지는 없다.

## 바로 써보기

```bash
cd ~/.claude/skills/paperlogy-copy-skill

# 걸리는 카피
echo "솔직히 이건 좋은 브랜드입니다 — 우리는 다릅니다" | python3 scripts/brandlogy_lint.py -
# → ERROR 2건, exit 1

# 통과하는 카피
echo "당신의 하루가 5분 짧아집니다." | python3 scripts/brandlogy_lint.py -
# → ERROR 0, exit 0
```

`exit 1`이면 그 카피는 미완성이다. 납품·발송·등록 전에 0으로 만든다.

## 파일

| 파일 | 언제 쓰나 |
|---|---|
| `SKILL.md` | 진입점. 작업 순서와 원칙 요약 |
| `COPYWRITING.md` | 원칙 전문. 워크플로우 상세 |
| `scripts/brandlogy_lint.py` | 슬로건·매니페스토·브랜드 카피·PPT 카피·메일 |
| `scripts/writing_lint.py` | 강의 원고·유튜브 대본·책 원고 등 긴 글 |
| `scripts/review_reply_lint.py` | 검토 회신을 보내기 전 |
| `scripts/coverage_ledger.py` | "전부 고쳐" 지시를 받았을 때 |

## 게이트가 잡는 것

줄표 · 이모지 · "솔직히" 류 강조 도입부 · 군더더기 부사 · 이중피동 ·
일본어투 · 번역체 · 대조말투 남발 · 카피 클리셰 · 느낌표 남발 ·
검토 회신에서 칭찬한 문장을 수정본에서 갈아치우는 것.

## 게이트가 못 잡는 것

End Benefit에 닿았는지, 낭독이 걸리는지, 브리프에 충실한지,
그리고 **클라이언트가 하지 않은 말을 지어내지 않았는지**.

마지막 항목이 가장 위험하다. 지어낸 문장일수록 문법이 완벽하고 읽기도 좋아서
검사 코드가 통과시킨다. 브리프 원문과 손으로 대조해야 걸린다.

그래서 각 게이트는 ERROR가 0이어도 끝에 체크리스트를 출력한다. 그 줄들은 넘기지 않는다.
