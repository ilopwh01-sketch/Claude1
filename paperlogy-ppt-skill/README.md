# 페이퍼로지 PPT 스킬 — 설치와 사용

pptxgenjs로 PPT를 만들고, 코드가 디자인 규칙을 검사하는 번들입니다.
Claude Code(또는 Claude Desktop)에 스킬로 붙여 쓰거나, 명령줄에서 직접 써도 됩니다.

---

## 1. 필요한 것

| 항목 | 필수 여부 | 없으면 |
|---|---|---|
| **Node.js** 18 이상 | 필수 | 빌드 자체가 안 됨 |
| **Python** 3.9 이상 | 필수 | 검사 스크립트가 안 돎 |
| **pptxgenjs** | 필수 | 빌드 불가 |
| **Pillow** (`pip install pillow`) | 필수 | 렌더 이미지 처리 실패 |
| **python-pptx** (`pip install python-pptx`) | 필수 | `coverage_ledger.py` 사용 불가 |
| **numpy** (`pip install numpy`) | 권장 | 이미지 내부 여백 검사(#23)만 건너뜀 |
| **Pretendard 폰트** | 권장 | 글자 폭이 달라져 일부 검사가 부정확해짐 |
| **LibreOffice** (`soffice`) | 권장 | 빌드 후 PNG 미리보기 생략 |
| **poppler** (`pdftoppm`) | 권장 | 위와 같음 |
| **PowerPoint (macOS)** | 선택 | 실제 렌더 확인 단계 생략. 다른 OS면 자동으로 건너뜀 |

### 설치

```bash
# 이 폴더에서
npm install pptxgenjs
pip install pillow python-pptx numpy

# macOS 렌더 도구 (선택)
brew install --cask libreoffice
brew install poppler

# 폰트: Pretendard 내려받아 설치
# https://github.com/orioncactus/pretendard
```

---

## 2. 첫 빌드로 확인하기

```bash
cp templates/paperlogy-ppt-template.js ./build-v01-test.js
python3 scripts/build_ppt.py ./build-v01-test.js
```

템플릿을 그대로 빌드하면 검사를 전부 통과하고 `샘플-발표자료-v01.pptx`가 나옵니다.
**그 상태가 정상 출발점입니다.** 여기서부터 데이터와 문구를 자기 것으로 바꿔 나가면 됩니다.

템플릿에 든 숫자와 문구는 **차트 종류를 보여주려고 만든 가상 예시**입니다.
실제 통계가 아니니 그대로 발표에 쓰지 말고 자기 데이터로 갈아 끼우세요.

### 빌드 단계

```
[0/5] 참고 덱 확인   개인 참고 파일이 있을 때만 동작. 없으면 그냥 통과
[1/5] 카피 검사      슬라이드의 모든 글자 (줄표·이모지·번역체·대조말투)
[2/5] pptx 생성      node로 빌드
[3/5] ppt_lint       좌표·색·겹침·여백 등 디자인 규칙 전수
[4/5] PNG 미리보기   LibreOffice가 있을 때
[5/5] 실렌더         macOS + PowerPoint가 있을 때만. 다른 환경은 자동으로 건너뜀
[6/6] 교차검수 안내  사람이 눈으로 보는 단계 (차단하지 않음)
```

### `--fast`는 언제 쓰나

```bash
python3 scripts/build_ppt.py ./build-v01-test.js --fast
```

`--fast`는 **[5/5] 실렌더와 [6/6] 안내만** 건너뜁니다. 고치고 다시 빌드하기를
반복하는 동안 PowerPoint가 매번 뜨는 게 번거로울 때 씁니다.
**검사 게이트는 `--fast`를 붙여도 그대로 다 돕니다.**

최종본은 `--fast` 없이 한 번 돌려서 실제 렌더까지 확인하세요.
macOS가 아니거나 PowerPoint가 없으면 [5/5]는 자동으로 건너뜁니다. 빌드는 멈추지 않습니다.

### 마지막 판정은 사람이 합니다

만든 사람이 자기 결과물을 통과시키는 구조는 반드시 한 번 뚫립니다.
게이트가 잡아주는 건 규칙 위반까지고, **카피가 좋은지·레이아웃이 매번 다른지·
카드 글자가 잘리지 않았는지는 눈으로 봐야 합니다.** 가능하면 만들지 않은 사람에게 보여주세요.

---

### build.js는 번들 루트에서 만듭니다

템플릿이 `fix-slidenum.py`와 `ppt_lint.py`를 **자기 옆에서** 찾기 때문에,
그 둘은 `scripts/`와 번들 루트 양쪽에 있습니다. `build.js`를 루트에 두면 그대로 돕니다.

---

## 3. 새 PPT 만들기

1. `templates/paperlogy-ppt-template.js`를 복사해 `build-v02-주제.js` 같은 이름으로 저장합니다
2. 데이터와 문구만 바꿉니다. **좌표·색·폰트 사양은 건드리지 않습니다**
3. 파일 끝의 `writeFile({ fileName: ... })`에 원하는 출력 이름을 넣습니다
4. `python3 scripts/build_ppt.py ./build-v02-주제.js`

검사에 걸리면 `GATES.md`에서 해당 번호를 찾아 고칩니다.

---

## 4. 경로 설정

스크립트와 배경 이미지는 `__dirname`(빌드 스크립트 자신의 위치) 기준으로 찾습니다.
그래서 번들(스크립트·템플릿·assets)을 통째로 옮기기만 하면 됩니다 — 흩어서 따로 옮기는 건 지원하지 않습니다.

파이썬 실행 파일 이름이 다르면 이렇게 지정합니다.

```bash
export PYTHON=python3.12
```

---

## 5. 검사 스크립트를 따로 쓰기

```bash
# PPT 코드·좌표 검사
python3 scripts/ppt_lint.py build-v02-주제.js v02-주제.pptx

# 슬라이드 카피 검사
python3 scripts/brandlogy_lint.py 카피.txt

# 일반 글 검사 (PPT 밖 원고용)
python3 scripts/writing_lint.py 원고.txt

# "전부 고쳐" 지시를 받았을 때 전 텍스트 블록 나열
python3 scripts/coverage_ledger.py v02-주제.pptx
```

확정본을 버전 없는 정본 이름으로 승격할 때는 다음처럼 씁니다.
저장 위치는 `PPT_GALLERY_DIR` 환경변수, `--gallery-dir` 인자, 없으면 `./output` 순으로 정해집니다.

```bash
python3 scripts/promote_ppt.py v02-주제.pptx "주제" --gallery-dir ./output
```

---

## 6. Claude 스킬로 붙이기

Claude Code에서 스킬로 쓰려면 이 폴더째 아래 위치에 둡니다.

```
~/.claude/skills/paperlogy-ppt/          # 모든 프로젝트에서 사용
<프로젝트>/.claude/skills/paperlogy-ppt/  # 그 프로젝트에서만 사용
```

`SKILL.md`의 `description`에 걸린 표현("PPT 만들어줘", "슬라이드 만들어" 등)이 나오면 자동으로 읽힙니다.

---

## 7. 문서 순서

| 문서 | 언제 |
|---|---|
| `SKILL.md` | 작업 시작 전. 원칙과 순서 |
| `DESIGN-SYSTEM.md` | 색·좌표·폰트·카드·차트 규격이 필요할 때 |
| `GATES.md` | 빌드가 막혔을 때. 검사 규칙 전수 |

---

## 8. 자주 막히는 곳

**빌드가 `[1/5]`에서 멈춘다**
카피에 줄표(— –)나 이모지가 있습니다. 주석에 넣은 것도 걸립니다.
카피 추출기가 소스 전체를 훑기 때문입니다. 콜론·쉼표·물결로 바꾸세요.

**`ppt_lint`가 "배경 누락" ERROR를 낸다**
`assets/Background_paperlogy.jpg`를 전 슬라이드 첫 줄에 넣어야 합니다.
템플릿의 `addBackground(s)`를 각 슬라이드에서 부르면 됩니다.

**"valign" ERROR가 잔뜩 나온다**
모든 `addText`에 `valign: "middle"`이 필요합니다.
기본값(위 정렬)은 글자가 상자 아래로 밀려나 이탈합니다.

**색이 ERROR로 막힌다**
승인 팔레트 밖의 파란 계열은 전부 막힙니다. `DESIGN-SYSTEM.md`의 팔레트 표에서 골라 쓰세요.

**PNG가 안 만들어진다**
LibreOffice(`soffice`)가 없거나 PATH에 없습니다. 빌드 자체는 정상 완료된 것이니 pptx를 직접 열어 확인하세요.
