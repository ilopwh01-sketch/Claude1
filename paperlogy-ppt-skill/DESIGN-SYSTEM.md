# Paperlogy PPT Design System

이 문서는 이 번들로 만드는 모든 덱의 **디자인 정본**이다.
좌표·색·pt 값은 `templates/paperlogy-ppt-template.js`의 실제 코드에서 뽑았다. 코드와 이 문서가 어긋나면 코드가 맞다.

---

## 1. 이 디자인 시스템의 원칙

1. **팔레트를 고르지 않는다.** 주제·고객사·강의 성격과 무관하게 모든 덱이 같은 색 체계(클라인블루 `002FA7` + 강조 오렌지 `FF7A00` + 그레이)를 쓴다. "이번 건은 색을 뭘로 할까"라는 질문 자체가 없다.
2. **카드는 선이 아니라 그림자로 뜬다.** 흰 카드의 외곽선은 0(`line: { type: "none" }`)이고, opacity 0.05짜리 아주 옅은 그림자만으로 배경에서 분리된다. 선을 그리면 화면이 시끄러워진다.
3. **모든 텍스트는 세로 가운데 정렬이다.** 예외 없이 `valign: "middle"`. 기본값(top)은 상단 인셋과 Pretendard 줄피치 때문에 글자가 박스 아래로 처져 보인다.
4. **좌표는 밴드로 고정돼 있다.** 헤더·본문·SO WHAT·하단 스트립의 y값은 슬라이드마다 다시 정하는 게 아니라 이미 정해져 있다. 슬라이드가 달라도 눈이 같은 자리를 찾는다.
5. **한 슬라이드 = 한 메시지 + 시각화 1개 + SO WHAT 한 줄.** 강조가 둘이면 강조가 사라진다.
6. **텍스트 카드만 나열하는 슬라이드는 미완성으로 본다.** 개념·구조도 플로우·매트릭스·다이어그램으로 시각화할 수 있다.
7. **차트의 모든 값에는 숫자가 붙는다.** 막대·점·세그먼트마다 데이터 라벨이 보여야 한다. 축만 보고 눈금을 읽게 하지 않는다.

---

## 2. 팔레트

### 정본 토큰 (`paperlogy-ppt-template.js`의 `C` 객체 그대로)

```javascript
const FONT = "Pretendard";
const FONT_M = "Pretendard Medium";
const C = {
  // 표준 블루 = 클라인 블루 
  brand: "002FA7", brandDeep: "001C64", accent: "FF7A00",
  brandT2: "4D6DC1", brandT3: "99ACDB", brandT4: "D9E0F2",
  brandPale: "EAEEF8",
  ink: "222222", text: "3A4654", mute: "5A6678",
  caption: "8A94A2", source: "5F6B78",
  white: "FFFFFF", surface2: "EFF2F6", surface3: "F4F6F9",
};
const AXIS_GREY = "B7BDC8";
const GRID_GREY = "D5DAE3";
```

| 토큰 | hex | 용도 |
|---|---|---|
| `brand` | `002FA7` | 메인 잉크. 챕터 라벨, 섹션 라벨, 주 계열 차트, 강조 막대, SO WHAT 라벨 |
| `brandDeep` | `001C64` | 거대 숫자, KPI 큰 값, 도넛 hole 수치. brand보다 한 단계 무거운 강조 |
| `accent` | `FF7A00` | 강조 1색. **비문자 요소 전용** (아래 참조) |
| `brandT2` | `4D6DC1` | 다계열 위계 2단 |
| `brandT3` | `99ACDB` | 다계열 위계 3단 |
| `brandT4` | `D9E0F2` | 다계열 위계 4단, 옅은 면 |
| `brandPale` | `EAEEF8` | 강조 카드 배경(슬라이드당 1곳) |
| `ink` | `222222` | 헤드라인, 본문 핵심 글자, 데이터 라벨 |
| `text` | `3A4654` | 서브타이틀, 범례, 보조 본문 |
| `mute` | `5A6678` | 비교군(하락·상대편) 색, 설명문, 축 값 라벨 |
| `caption` | `8A94A2` | 최약 위계 텍스트, 페이지 번호 |
| `source` | `5F6B78` | 하단 Source 문구 |
| `white` | `FFFFFF` | 카드 fill, 차트 영역 fill |
| `surface2` | `EFF2F6` | SO WHAT 띠 fill |
| `surface3` | `F4F6F9` | 보조 면 |
| `AXIS_GREY` | `B7BDC8` | 차트 축 baseline |
| `GRID_GREY` | `D5DAE3` | 차트 값 grid, 구분선 |

보조 그레이(토큰 밖이지만 코드가 실제로 쓰는 값): 칩·미니 카드 fill `F6F7FB`, 막대 트랙·얇은 구분선 `EEF0F4`, KPI 세로 구분선 `DDE1E8`.

### 오렌지 `FF7A00`은 글자에 쓰지 않는다

| 쓸 수 있는 곳 | 쓰면 안 되는 곳 |
|---|---|
| 탭·바·면·밑줄 같은 비문자 도형, 차트 하이라이트 막대 | 글자, 숫자, 라벨, 아이콘 안 텍스트 (크기 무관) |

이유는 대비다. 밝은 배경 위 오렌지의 명도 대비는 약 **2.4:1**로, WCAG의 대형 텍스트 최소치 3:1에도 못 미친다. 화면·인쇄 어느 쪽에서도 읽기 나쁘다. 텍스트 강조가 필요하면 `brand` 또는 `brandDeep`을 쓴다. 오렌지는 슬라이드당 핵심 1곳, 면적 최소.

### 폐기 색 (쓰면 안 됨)

| hex | 정체 |
|---|---|
| `D97757` | 옛 코랄 강조색 |
| `292524` | 옛 차콜 |
| `0B2E4F` | 옛 딥네이비 |
| `1C6DD0` | 옛 메디컬블루 |
| `4F6EF1` | 옛 형광블루 계열 |
| `EA5EC1` / `FFEAF6` | 핑크 계열, 시멘틱 색으로 금지 |
| `16A34A` | 녹색, 시멘틱 색으로 금지 |
| `EF4444`, `F97316` | 경고성 채도색, 금지 |

승인 팔레트에 없는 **즉석 블루 틴트**를 만들어 쓰는 것도 금지다. 블루는 `002FA7 / 001C64 / 4D6DC1 / 99ACDB / D9E0F2 / EAEEF8` 여섯 개가 전부다. 웜그레이·웜화이트·베이지 배경도 쓰지 않는다. 주제별로 팔레트를 분기하지 않는다.

### 시멘틱 규칙

| 의미 | 색 |
|---|---|
| 상승, 증가, 우리 편, 주 계열 | `brand` / `brandDeep` |
| 하락, 감소, 상대 편, 비교군 | `mute` / `caption` |
| before → after | `caption` → `brand` |
| 3단계 이상 위계 | `brand` → `brandT2` → `brandT3` → `brandT4` (진 → 연) |

---

## 3. 폰트·타이포

폰트는 **Pretendard** 하나다. `fontFace: "Pretendard"`, 굵은 중간 웨이트가 필요하면 `"Pretendard Medium"`.

### 용도별 크기

| 용도 | pt | 굵기 | 색 | 비고 |
|---|---|---|---|---|
| Cover Title | 44~48 | bold | white | 표지 전용 |
| Slide Headline | **26** | bold | `ink` | h 0.55 |
| Subtitle | 12 | regular | `text` | h 0.303 |
| Chapter 라벨 | 10 | bold | `brand` | `charSpacing: 2` |
| 섹션 라벨 (KEY INSIGHT 등) | 9 | bold | `brand` | `charSpacing: 3` |
| 카드 헤드 (한 줄 요약) | 13~14 | bold | `ink` | |
| 거대 숫자 | **56** | bold | `brandDeep` | `charSpacing: -1` |
| KPI 큰 값, 도넛 hole 수치 | 22 | bold | `brandDeep` | |
| 칩 안 값 | 16 | bold | `brand` | |
| 카드 본문, 한 줄 설명 | 10~11 | regular | `mute` / `text` | |
| 차트 카테고리 축 라벨 | 10 | Medium | `ink` | |
| 차트 값 축 라벨 | 9 | regular | `mute` | |
| 데이터 라벨 | 9 | bold | `ink` | |
| 범례 | 10 | regular | `text` | |
| 미세 라벨, 칩 캡션 | 8 | regular/bold | `mute` / `caption` | |
| Source, 페이지 번호 | 8 | regular | `source` / `caption` | |

### 자간 (charSpacing)

| 대상 | 값 |
|---|---|
| 대문자 영문 라벨 (CHAPTER, KEY INSIGHT, COMPARISON) | +2 ~ +3 |
| 거대 숫자 | -1 |
| 한글 본문 | 0 또는 -0.3 |
| 한글 헤드라인 | 0 (기본), 조이려면 -0.5까지 |

**한글에 양수 자간을 주지 않는다.** 한글 대문자 라벨이라는 개념 자체가 없으므로 라벨은 영문으로 쓰거나 자간 0으로 둔다.

### 행간·줄바꿈

- 본문 행간 = 폰트 크기 × 1.45~1.5, 헤드라인 = × 1.2
- 한 줄 25~35자, **어절 단위로** 끊는다
- 헤드라인이 두 줄이면 위를 길게, 아래를 짧게
- 한글 본문은 같은 자리 영문보다 1pt 작게 (헤드라인은 동일)

### 문장부호

- 헤드라인 마침표: **코드가 자동으로 붙인다.** `addHeader`가 끝이 `.?!`가 아니면 마침표를 붙여 넣으므로 원고에 안 써도 된다
- 가운뎃점 `·` 적극 사용 (예: `01 · 콘텐츠 분야별 수출`)
- 물결 `~`로 범위 표기
- 숫자와 단위는 띄어쓴다 (`250 조원`), 단 한글 한 글자 단위는 붙인다 (`1,700만명`)
- **줄표(— –) 금지.** 콜론·쉼표·물결·괄호로 대체
- 한글 따옴표 `「」『』` 금지, italic 금지(한글은 특히 깨진다), 이모지 금지

---

## 4. 레이아웃 좌표

### 슬라이드

```javascript
pres.defineLayout({ name: "BRANDLOGY_169", width: 13.333, height: 7.5 });
pres.layout = "BRANDLOGY_169";
```

단위는 전부 인치. 16:9.

| 항목 | 값 |
|---|---|
| 좌 마진 | 0.422 |
| 우 마진 (콘텐츠 우측 끝) | 12.912 |
| 가용 폭 | 12.49 |

배경은 모든 슬라이드 **첫 줄에** 깐다.

```javascript
function addBackground(s) {
  s.addImage({ path: BG_PATH, x: 0, y: 0, w: 13.333, h: 7.5 });
}
```

배경 이미지(`assets/Background_paperlogy.jpg`)에 로고가 우측 상단에 이미 박혀 있다. **로고 텍스트·이미지를 따로 추가하지 않는다.**

### 헤더 3요소

```javascript
function addHeader(s, chapter, headline, subtitle) {
  s.addText(chapter, {
    x: 0.422, y: 0.306, w: 8, h: 0.3,
    fontFace: FONT, fontSize: 10, bold: true, color: C.brand, charSpacing: 2, valign: "middle" });
  s.addText(/[.?!]$/.test(headline) ? headline : headline + ".", {  // 대제목 마침표 필수 
    x: 0.422, y: 0.851, w: 12.262, h: 0.55,
    fontFace: FONT, fontSize: 26, bold: true, color: C.ink, valign: "middle"
  });
  if (subtitle) {
    s.addText(subtitle, {
      x: 0.422, y: 1.472, w: 12.262, h: 0.303,
      fontFace: FONT, fontSize: 12, color: C.text, valign: "middle" });
  }
}
```

| 요소 | x | y | w | h |
|---|---|---|---|---|
| Chapter (`NN · 카테고리`) | 0.422 | 0.306 | 8 | 0.3 |
| Headline | 0.422 | 0.851 | 12.262 | 0.55 |
| Subtitle | 0.422 | 1.472 | 12.262 | 0.303 |

헤드라인은 사실 진술이 아니라 **결론**이다. "글로벌 출판 시장 매출"이 아니라 "미국이 글로벌 25% 점유, 중국과 격차 1.4배".

### 본문 카드 (표준 2단)

`paperlogy-ppt-template.js`가 실제로 쓰는 정본 조합이다. 좌측이 차트·도넛, 우측이 인사이트·KPI.

| 카드 | x | y | w | h | 우측 끝 |
|---|---|---|---|---|---|
| 좌측 | 0.422 | 2.20 | 7.95 | 3.85 | 8.372 |
| 우측 | 8.567 | 2.20 | 4.345 | 3.85 | 12.912 |

두 카드 사이 gap 0.195, 카드 하단은 6.05에서 끝난다.

```javascript
box(s2, 0.422, 2.20, 7.95, 3.85);
box(s2, 8.567, 2.20, 4.345, 3.85);
```

### SO WHAT 띠

```javascript
function addSoWhat(s, msg) {
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.422, y: 6.20, w: 12.49, h: 0.40,
    fill: { color: C.surface2 }, line: { type: "none" }, rectRadius: 0.06
  });
  s.addText([
    { text: "SO WHAT", options: { bold: true, color: C.brand, fontSize: 10, charSpacing: 2 } },
    { text: "     " },
    { text: msg, options: { color: C.ink, fontSize: 11 } }
  ], {
    x: 0.422, y: 6.20, w: 12.49, h: 0.40,
    fontFace: FONT,
    align: "center", valign: "middle"
  });
}
```

| 항목 | 값 |
|---|---|
| x / y / w / h | 0.422 / 6.20 / 12.49 / **0.40** |
| fill | `surface2` (`EFF2F6`) |
| line | none |
| rectRadius | 0.06 |
| 정렬 | 가로 가운데, 세로 가운데 |
| 위 카드와 gap | **0.15** (6.05 → 6.20). 더 붙이지도 더 띄우지도 않는다 |

라벨 문구는 슬라이드 성격에 따라 바꿔도 되지만(예: `KEY TAKEAWAY`) 위치·크기·형식은 고정이다.

### Source·페이지 번호

```javascript
function addBottomStrip(s, pageNum, source) {
  s.addText(source, {
    x: 0.535, y: 6.85, w: 11, h: 0.3,
    fontFace: FONT, fontSize: 8, color: C.source, valign: "middle" });
  // 페이지 번호 = PowerPoint 네이티브 자동 슬라이드 번호(placeholder).
  // 고정 텍스트 X: 슬라이드를 다른 PPT에 붙여넣으면 위치에 맞게 자동 갱신됨.
  // pageNum 인자는 기존 호출부 호환 위해 받되 미사용.
  s.slideNumber = {
    x: 12.45, y: 6.85, w: 0.5, h: 0.3,
    fontFace: FONT, fontSize: 8, color: C.caption, align: "right"
  };
}
```

- 페이지 번호는 **반드시 `s.slideNumber` 네이티브 placeholder**로 넣는다. `addText("03")` 같은 고정 텍스트는 금지
- 빌드 후 `scripts/fix-slidenum.py`를 돌려 번호 필드에 서식을 주입한다. 안 하면 PowerPoint가 마스터 기본 서식으로 덮어 번호만 다른 폰트로 보인다
- Source는 필수다. 인용 수치가 있으면 출처를 적고, 기사 속 "지난달·어제" 같은 상대 날짜는 **절대 날짜로 변환**해서 쓴다

### RESERVED Y BANDS

이 밴드를 침범하지 않는다.

| 밴드 | y 시작 | y 끝 | 내용 |
|---|---|---|---|
| 상단 여백 | 0 | 0.306 | 비움 |
| Chapter | 0.306 | 0.606 | 챕터 라벨 |
| 여백 | 0.606 | 0.851 | 비움 |
| Headline | 0.851 | 1.401 | 대제목 |
| Subtitle | 1.472 | 1.775 | 리드 한 줄 |
| 여백 | 1.775 | 2.20 | 비움 |
| **Box System (본문)** | **2.20** | **6.05** | 카드·차트·도식. 콘텐츠 max y ≤ 6.05 |
| 여백 | 6.05 | 6.20 | gap 0.15 |
| SO WHAT | 6.20 | 6.60 | 결론 띠 |
| 여백 | 6.60 | 6.85 | 비움 |
| Bottom Strip | 6.85 | 7.15 | Source, 페이지 번호 |

---

## 5. Box System P1~P7

부모 영역은 `x 0.422 / y 2.20 / w 12.49 / h 3.85`. 이걸 분할해서 쓴다.

공통 규칙: fill white, line none, rectRadius 0.18(큰) 또는 0.14(작은), 그림자 factory, **박스 사이 gap 가로 0.20 / 세로 0.15**, 안쪽 padding 0.20 이상.

| 패턴 | 구성 | 좌표 | 언제 쓰나 |
|---|---|---|---|
| **P1** Single | 풀폭 1장 | x 0.422, y 2.20, w 12.49, h 3.85 | 큰 도식 1개, 타임라인, 풀폭 매트릭스, 채팅 목업 |
| **P2L** 좌우 1:1 | L / R | L x 0.422 w 6.145 · R x 6.767 w 6.145 · h 3.85 | 정면 비교(A vs B), before/after |
| **P2H** 상하 1:1 | T / B | T y 2.20 h 1.85 · B y 4.20 h 1.85 · w 12.49 | 위 KPI 4개 + 아래 해설, 상단 결론 + 하단 근거 |
| **P3** 3분할 | L / M / R | x 0.422 / 4.645 / 8.868 · w 4.043 · h 3.85 | 동등한 3요소(3단계, 3페르소나, 3전략) |
| **P4** 2×2 | TL TR BL BR | x 0.422 / 6.767 · y 2.20 / 4.20 · w 6.145 h 1.85 · r 0.14 | 동등한 4요소, 2×2 매트릭스 |
| **P5** 비대칭 5:7 | 좁은 좌 + 넓은 우 | L x 0.422 w 4.95 · R x 5.572 w 7.34 · h 3.85 | 핵심 메시지(좌) + 큰 시각화(우) |
| **P6** 비대칭 7:5 | 넓은 좌 + 좁은 우 | L x 0.422 w 7.34 · R x 7.962 w 4.95 · h 3.85 | 차트(좌) + 인사이트 카드(우) |
| **P7** 혼합 | 큰 좌 + 우측 상하 2 | L x 0.422 w 7.34 h 3.85 · TR x 7.962 y 2.20 h 1.85 · BR x 7.962 y 4.20 h 1.85 | 메인 시각화 + 보조 지표 다수 |
| **표준 2단** | 차트 + 인사이트 | L x 0.422 w 7.95 · R x 8.567 w 4.345 · h 3.85 | `paperlogy-ppt-template.js`가 쓰는 실전 정본. P6보다 좌측을 더 넓게 잡은 65:35 |

선택 기준: 풀폭 1개 → P1 / 비교 → P2L / 데이터+인사이트 → P2H·P5·P6·표준 2단 / 동등 3개 → P3 / 동등 4개 → P4 / 핵심+디테일 → P5·P6 / 메인+보조 다수 → P7.

**연속한 슬라이드에서 같은 패턴을 반복하지 않는다.** 판이 계속 같으면 덱 전체가 게을러 보이고, 린트도 레이아웃 지문 중복을 잡는다.

---

## 6. 카드 스타일

```javascript
const sContainer = () => ({ type: "outer", color: "000000", blur: 12, offset: 2, angle: 90, opacity: 0.05 });

function box(s, x, y, w, h, o = {}) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h,
    fill: { color: o.fill || C.white },
    line: { type: "none" },
    rectRadius: o.r || 0.18,
    shadow: o.shadow !== false ? sContainer() : undefined
  });
}
```

### radius 3단계

| 단계 | 값 | 대상 |
|---|---|---|
| 큰 | 0.18 | 본문 흰 카드 |
| 중간 | 0.10 ~ 0.14 | 작은 분할 카드(P4), 말풍선, 컨테이너 |
| 작은 | 0.06 ~ 0.08 | SO WHAT 띠, 칩, 미니 카드, 막대 트랙 |

3단계를 넘는 라운드 값을 새로 만들지 않는다.

### shadow

| 값 | 표준 | 밀도 높은 목업(말풍선 등) |
|---|---|---|
| type | outer | outer |
| color | 000000 | 000000 |
| blur | 12 | 9 |
| offset | 2 | 1.2 |
| angle | 90 | 90 |
| opacity | **0.05** | 0.05 |

opacity는 0.10을 넘기지 않는다. 그림자는 "카드가 떠 있다"는 힌트지 장식이 아니다.
**shadow는 반드시 factory 함수로 매번 새 객체를 만든다.** 같은 객체를 여러 도형에 재사용하면 pptxgenjs가 일부만 렌더한다.

### 내부 padding

| 항목 | 값 |
|---|---|
| 좌우 안쪽 padding | 최소 0.20, 인사이트 카드는 0.30 |
| 상단 첫 요소 y | 카드 y + 0.14 ~ 0.20 |
| **하단 padding** | **최소 0.18** (어두운 카드는 0.25) |
| 텍스트 박스 안전 여유 | 0.10 |
| 노드·요소 사이 간격 | 최소 0.20 |

`paperlogy-ppt-template.js`의 인사이트 카드는 이렇게 잡는다.

```javascript
const CX = 8.567;       // 카드 좌측 x
const CW = 4.345;       // 카드 폭
const PAD = 0.30;       // 내부 좌우 패딩
const ix = CX + PAD;    // 내부 컨텐츠 x
const iw = CW - PAD * 2;// 내부 컨텐츠 w
```

### 콘텐츠 max y

본문 콘텐츠는 **y 6.05를 넘지 않는다.** 카드 안 마지막 요소의 아래끝(y + h)이 6.05 이하여야 SO WHAT 띠와 겹치지 않는다.

### 카드 안 밀도

- 카드 위쪽에만 내용이 몰리고 아래가 비면 안 된다. 하단까지 채우거나 카드 높이를 줄인다
- 좌우도 마찬가지다. 한쪽에 텅 빈 세로 기둥이 생기면 폭을 줄이거나 내용을 확장한다
- 카드를 키우고 남는 자리를 큰 글씨로 때우지 않는다

---

## 7. 차트

### CHART_CLEAN (모든 차트 공통, 그대로 스프레드해서 쓴다)

```javascript
const AXIS_GREY = "B7BDC8";
const GRID_GREY = "D5DAE3";
const CHART_CLEAN = {
  chartArea: { fill: { color: C.white }, border: { color: C.white, pt: 0 } },
  plotArea: { fill: { color: C.white }, border: { color: C.white, pt: 0 } },
  catAxisLineShow: true,
  valAxisLineShow: true,
  catAxisLineColor: AXIS_GREY,
  valAxisLineColor: AXIS_GREY,
  catAxisLineSize: 0.75,
  valAxisLineSize: 0.75,
  valGridLine: { color: GRID_GREY, style: "solid", size: 0.5 },
  catGridLine: { style: "none" },
  catAxisMajorTickMark: "none",
  catAxisMinorTickMark: "none",
  valAxisMajorTickMark: "none",
  valAxisMinorTickMark: "none",
};
```

정리하면: 차트 외곽 박스 없음, tick mark 없음, 카테고리 축 grid 없음. 대신 **축 baseline은 살리고**(`B7BDC8` 0.75pt), **값 grid는 아주 희미하게**(`D5DAE3` 0.5pt) 남긴다. 완전히 지우면 값을 읽을 기준이 사라진다.

### 데이터 라벨은 필수다

모든 차트(Bar·Column·Line·Doughnut·Pie)에 값이 보여야 한다. 예외 없다.

```javascript
showValue: true,            // 또는 showPercent: true (도넛·파이)
dataLabelFontFace: FONT,
dataLabelFontSize: 9,
dataLabelFontBold: true,
dataLabelColor: C.ink,
dataLabelPosition: "outEnd" // bar/line/column: "outEnd" · doughnut: "ctr"
```

`valAxisMajorUnit`은 데이터 max에 맞춰 촘촘하게(2~10) 잡는다.

### 차트 색 위계

| 상황 | chartColors |
|---|---|
| 단일 계열 | `[C.brand]` |
| 2계열 비교 | `[C.mute, C.brand]` (강조 대상이 brand) |
| 3계열 이상 위계 | `[C.brandDeep, C.brand, C.brandT2, C.brandT3, C.brandT4]` (진 → 연) |
| 상승 / 하락 | `brand` / `mute` |
| before / after | `caption` / `brand` |

무지개색·채도색을 계열 구분에 쓰지 않는다. 위계는 같은 블루의 명도로 만든다.

### 막대 차트 예시 (template.js 실코드)

```javascript
s2.addChart(pres.charts.BAR, [ /* ... */ ], {
  x: 0.65, y: 2.40, w: 7.50, h: 3.45,
  ...CHART_CLEAN,
  catAxisLabelFontFace: FONT_M, catAxisLabelFontSize: 10,
  catAxisLabelColor: C.ink,
  valAxisLabelFontFace: FONT, valAxisLabelFontSize: 9,
  valAxisLabelColor: C.mute,
  valAxisMajorUnit: 5,
  valAxisMinVal: 0,
  valAxisMaxVal: 30,
  showLegend: true, legendPos: "b",
  legendFontFace: FONT, legendFontSize: 10, legendColor: C.text,
  barDir: "bar",
  barGrouping: "clustered",
  chartColors: [C.mute, C.brand],
  showValue: true,
  dataLabelFontFace: FONT, dataLabelFontSize: 9,
  dataLabelFontBold: true, dataLabelColor: C.ink,
  dataLabelPosition: "outEnd"
});
```

### 도넛 규격

```javascript
s3.addChart(pres.charts.DOUGHNUT, [
  { name: "식품 점유", labels: ["오프라인", "온라인"], values: [44, 56] }
], {
  x: dx1, y: dy, w: dw, h: dh,
  ...CHART_CLEAN,
  showLegend: false,
  chartColors: [C.mute, C.brand],
  dataLabelFontFace: FONT, dataLabelFontSize: 10, dataLabelFontBold: true,
  dataLabelColor: C.white,
  showPercent: true,
  showValue: false,
  dataLabelPosition: "ctr",
  holeSize: 56,
  showTitle: false
});
```

| 항목 | 값 |
|---|---|
| holeSize | **56** (65는 링이 얇아져 작은 쪽 조각 라벨이 흰 hole에 물린다) |
| showTitle | false (차트 자체 제목 대신 카드 헤드로 쓴다) |
| showLegend | false (범례는 카드 하단에 도형+텍스트로 직접 그린다) |
| 라벨 | `showPercent: true`, 10pt bold, `white`, 위치 `ctr` |
| 도넛 크기 예시 | w 3.50 / h 2.20 |

**hole 가운데는 비우지 않는다.** 두 줄을 얹되, **링이 이미 말한 숫자를 중앙에서 또 말하지 않는다.**
같은 %를 두 번 쓰면 중앙 숫자와 조각 라벨이 좁은 링에서 자리 싸움을 하고, 작은 쪽 라벨이
흰 hole에 물려 잘린다. 역할을 나눈다: **링은 비율, 중앙은 무엇에 대한 비율인지.**

```javascript
s3.addText("식품", {                    // 중앙 1행: 대상 (숫자 아님)
  x: dx1 + 0.3, y: dy + dh / 2 - 0.26, w: dw - 0.6, h: 0.30,
  fontFace: FONT, fontSize: 15, bold: true, color: C.brandDeep,
  align: "center", valign: "middle"
});
s3.addText("온라인 우세", {             // 중앙 2행: 방향
  x: dx1 + 0.3, y: dy + dh / 2 + 0.04, w: dw - 0.6, h: 0.22,
  fontFace: FONT, fontSize: 9, color: C.mute,
  align: "center", valign: "middle", charSpacing: 1
});
```

**이 겹침은 차트 내부 좌표라 `ppt_lint`가 구조적으로 못 잡는다.** 도넛을 쓰면 렌더 PNG를
반드시 눈으로 열어 작은 쪽 조각 라벨이 hole 경계에 걸치지 않았는지 확인한다.

### stacked 비교 막대는 `rect`로

두 조각이 딱 붙어야 한다. `roundRect`로 그리면 사이에 흰 갭이 생긴다.

```javascript
s3.addShape(pres.ShapeType.rect, {
  x: barX, y: barY, w: krW, h: barInnerH,
  fill: { color: C.brand }, line: { type: "none" }
});
s3.addShape(pres.ShapeType.rect, {
  x: barX + krW, y: barY, w: jpW, h: barInnerH,
  fill: { color: C.mute }, line: { type: "none" }
});
```

반대로 **단독 진행 막대**(트랙 위에 얹는 막대)는 `roundRect` + `rectRadius: 0.05`로 끝을 둥글게 한다.

### 차트를 이미지로 박을 때

matplotlib·PIL로 렌더한 PNG를 카드에 넣을 경우, 통짜 슬라이드 PNG만 보지 말고 **그 이미지를 단독으로 열어** 내부 라벨과 데이터 마커가 겹치지 않는지 눈으로 확인한다. 좌표 기반 검사로는 이미지 내부를 못 잡는다.

---

## 8. template.js가 제공하는 헬퍼

`templates/paperlogy-ppt-template.js`에 실제로 정의된 것만이다. 다른 이름의 헬퍼는 없으므로 필요하면 직접 만든다.

| 이름 | 시그니처 | 하는 일 |
|---|---|---|
| `C` | 객체 | 색 토큰 테이블 |
| `FONT` / `FONT_M` | 문자열 | `"Pretendard"` / `"Pretendard Medium"` |
| `AXIS_GREY` / `GRID_GREY` | 문자열 | 차트 축·grid 색 |
| `CHART_CLEAN` | 객체 | 모든 차트에 스프레드하는 공통 옵션 |
| `sContainer()` | `() => shadowObj` | 카드 그림자 객체를 **매 호출마다 새로** 만든다 |
| `SKILL_DIR` | 상수 | 번들 루트. `PAPERLOGY_SKILL_DIR` 환경변수 > 상위 폴더 > 현재 폴더 순으로 자동 탐색 |
| `BG_PATH` | 상수 | `SKILL_DIR/assets/Background_paperlogy.jpg` |
| `addBackground(s)` | `(slide)` | 배경 이미지를 슬라이드 전면에 깐다. 모든 슬라이드 첫 줄 |
| `addHeader(s, chapter, headline, subtitle)` | `(slide, string, string, string?)` | 챕터 라벨 + 헤드라인(마침표 자동 부착) + 서브타이틀. subtitle은 생략 가능 |
| `box(s, x, y, w, h, o)` | `(slide, num, num, num, num, opts?)` | 흰 카드. `o.fill` 색 교체, `o.r` 라운드 교체, `o.shadow === false`면 그림자 제거 |
| `addSoWhat(s, msg)` | `(slide, string)` | 하단 결론 띠 |
| `addBottomStrip(s, pageNum, source)` | `(slide, num, string)` | Source 텍스트 + `slideNumber` placeholder 설정. `pageNum`은 호환용 인자로 실제로는 안 쓴다 |

### 빌드 꼬리 (그대로 복사할 것)

```javascript
pres.writeFile({ fileName: "v01-example.pptx" })
  .then((fn) => {
    const _cp = require("child_process");
    const PY = process.env.PYTHON || "python3";
    const SC = _path.join(SKILL_DIR, "scripts");
    _cp.execSync(`${PY} "${_path.join(SC, "fix-slidenum.py")}" "${fn}"`, { stdio: "inherit" });
    try { _cp.execSync(`${PY} "${_path.join(SC, "ppt_lint.py")}" "${__filename}" "${fn}"`, { stdio: "inherit" }); }
    catch (e) { console.log("ppt_lint ERROR: 위 목록을 0으로 고쳐 다시 빌드할 것."); process.exit(1); }
    console.log(`빌드 완료: ${fn}`);
  })
  .catch((err) => { console.error("빌드 실패:", err); process.exit(1); });
```

파일명은 **버전 번호를 맨 앞에** 둔다. 산출물 `vNN-주제.pptx`, 스크립트 `build-vNN-주제.js`. 정렬이 편해진다.

### 채팅 장면 템플릿 (`templates/chat-slide-template.js`)

대화 화면 목업이 주인공인 슬라이드용 변형이다. 우측 인사이트 카드가 없고 본문 전체를 채팅 컨테이너로 쓴다.

| 차이점 | 값 |
|---|---|
| `addHeader(s, chapter, headline)` | 인자 3개. 서브타이틀 없음, 헤드라인 24pt / y 0.80, 마침표 자동 부착 없음 |
| `addBottomStrip(s, source)` | 인자 2개. `pageNum` 없음 |
| 채팅 컨테이너 | x 0.422 / y 1.56 / w 12.49 / h 4.5, radius 0.10 |
| 2단 구분선 | x 6.66, y 2.12, h 3.74, `D5DAE3` 0.75pt |
| 좌 컬럼 / 우 컬럼 | 0.72~6.18 / 6.92~12.18 |
| 말풍선 행 간격 | 0.46 (버블 h 0.38) |

```javascript
function bubble(s, who, text, y, cL, cR) {
  const mine = who === "나", H = 0.38;
  const len = [...text].length;
  const w = Math.min(cR - cL, len * 0.125 + 0.42);
  const bx = mine ? cR - w : cL;
  s.addShape(pres.ShapeType.roundRect, { x: bx, y: y, w: w, h: H, fill: { color: mine ? C.brand : C.white }, line: mine ? { type: "none" } : { color: C.border, width: 1 }, rectRadius: 0.10, shadow: sContainer() });
  s.addText(text, { x: bx + 0.14, y: y, w: w - 0.28, h: H, fontFace: FONT, fontSize: 9.5, color: mine ? C.white : C.ink, valign: "middle" });
}
```

내 말풍선은 컬럼 우측 정렬 + brand fill + 흰 글자, 상대 말풍선은 좌측 정렬 + 흰 fill + 얇은 테두리. 폭은 글자수에 비례해 늘어나되 컬럼 폭을 넘지 않는다. 채팅 목업에는 화자 아바타를 넣어 누가 말하는지 한눈에 보이게 한다.

채팅 템플릿의 중립색 토큰 일부(`text`, `caption`, `source`, `surface2`)는 값이 조금 다르지만, 브랜드 컬러와 좌표 규격은 동일하다. 새 덱은 `paperlogy-ppt-template.js`의 `C`를 정본으로 쓴다.

---

## 9. 12 컬럼 그리드

| 항목 | 값 |
|---|---|
| 가용 폭 | 12.489 |
| 컬럼 수 | 12 |
| 컬럼 사이 gap | 0.10 |
| 컬럼 1개 폭 | **0.949** |

### n-up 카드 폭

| 배치 | 컬럼 수 | 카드 폭 |
|---|---|---|
| 2-up | 6 | 6.193 |
| 3-up | 4 | 4.095 |
| 4-up | 3 | 3.046 |
| 6-up | 2 | 1.998 |

계산식: `카드 폭 = 컬럼수 × 0.949 + (컬럼수 - 1) × 0.10`

### 비대칭 비율

| 비율 | 용도 |
|---|---|
| **5:7** | 가장 자주 쓴다. 좁은 메시지 + 넓은 시각화 |
| 7:5 | 넓은 차트 + 좁은 인사이트 (P6) |
| 4:8 | 라벨 열 + 본문 |
| 3:9 | 사이드 인덱스 + 본문 |
| 2:10 | 아이콘 열 + 본문 |

완전 대칭(6:6)만 반복하면 차가워 보인다. 의도된 비대칭을 섞는다.

### 광학 정렬

- 큰 도형 옆에 작은 도형을 둘 때는 0.02~0.05 들여쓴다
- 텍스트를 도형 우측에 붙일 때 좌측 padding 0.18
- 수학적으로 맞춘 정렬이 눈에는 어긋나 보일 수 있다. 의심되면 렌더 이미지로 확인한다
- 여러 카드의 좌·우 끝은 슬라이드 공통 마진(0.422 / 12.912)에 맞춘다

---

## 10. 하면 안 되는 것

### 구도·장식

- **좌측 세로 액센트 바** (카드 왼쪽에 색 띠 붙이기)
- **풀폭 컬러 바** (헤더나 푸터에 통짜 색 띠)
- 제목 아래 밑줄 라인
- 베이지·크림 배경, 지정 배경 이미지 외 배경
- 중앙 정렬 도배 (본문은 좌측 정렬이 기본, 가운데는 SO WHAT·도넛 라벨 같은 국소 요소만)
- **흰 카드 안에 또 흰 박스** (구분이 필요하면 `surface2`·`F6F7FB` 같은 옅은 면이나 얇은 구분선으로)
- 카드 안에 칩을 다닥다닥 붙이기 (옅은 구분선 리스트로 바꾼다)
- 강조를 2개 이상 (`brandPale` 강조 카드는 슬라이드당 1개)
- fill 색 5종 초과, line 두께 3단계 초과, radius 3단계 초과

### 텍스트

- **italic 한글** (자형이 깨진다)
- 12pt 미만 + 옅은 색 조합
- 이모지 (파일·대화 아이콘 같은 최소 예외 외 전부)
- **원형 숫자 ①②③** (도형 원 + 숫자 텍스트로 그린다)
- **줄표 — –** (콜론·쉼표·물결로)
- 한글에 양수 자간, 한글 대문자 라벨
- 헤드라인이 사실 진술 (결론으로 바꾼다)
- 자동 슬라이드 번호 대신 고정 텍스트로 페이지 번호 박기
- 배경에 이미 있는 로고를 텍스트·이미지로 또 추가

### 색

- 오렌지 `FF7A00`로 글자·숫자 쓰기
- 승인 팔레트 밖 즉석 hex, 특히 임의로 만든 블루 틴트
- 핑크·녹색·빨강 같은 채도색을 시멘틱으로 쓰기
- 무지개색 계열 구분
- hex에 `#` 접두사 붙이기, 8자리 hex(알파 채널) 쓰기

### 시각화

- **텍스트 카드만 줄줄 나열** (시각화 0인 슬라이드). 개념 슬라이드도 플로우·매트릭스·다이어그램으로 그릴 수 있다
- **pie·doughnut 5조각 이상** (4조각까지, 그 이상은 bar로)
- 같은 차트 타입 4회 이상 반복, 인접 3장에 같은 카테고리 2개 이상
- 슬라이드당 다이어그램 2개 이상
- 노드 12개 초과, 엣지 25개 초과
- 의미 없는 화살표, SmartArt처럼 보이는 도형 조합
- 데이터 라벨 없는 차트
- 노드·요소 간격 0.20 미만, 텍스트끼리 또는 텍스트와 도형이 겹침
- 도형 종류 5개 초과, 곡선 과용

---

## 11. pptxgenjs 알려진 함정

| # | 증상 | 대처 |
|---|---|---|
| 1 | **중첩 그림자가 일부만 렌더된다** | shadow 객체를 재사용하지 말고 `sContainer()` 같은 factory로 호출마다 새로 만든다 |
| 2 | **ELBOW connector 자동 라우팅이 안 된다** | L자 연결선은 LINE 두 조각으로 직접 그린다. 사선 연결 금지, 분기는 엘보 트리로 |
| 3 | **RHOMBUS(마름모) 안 텍스트가 모서리에서 잘린다** | `valign: "middle"` + 4자 이하 짧은 단어. 길면 도형 밖에 라벨 |
| 4 | trapezoid 미지원 | 피라미드·퍼널은 RECTANGLE의 폭 비율을 단계적으로 줄여 쌓는다 (1.0 → 0.85 → 0.65 → 0.45 → 0.30) |
| 5 | SmartArt 미지원 | 모든 다이어그램은 Shape + Line + Text 조합으로 직접 그린다 |
| 6 | roundRect 위에 액센트 바를 겹치면 모서리가 삐져나온다 | 상단 요소는 `rect`로 쓰거나 바를 없앤다 |
| 7 | `LAYOUT_WIDE`가 환경마다 다르게 잡힌다 | 반드시 `defineLayout({ width: 13.333, height: 7.5 })`를 명시 |
| 8 | 카드 위에 RECTANGLE을 깔면 카드 모서리가 가려진다 | 카드를 **먼저** 그리고 콘텐츠를 그 위에 올린다 |
| 9 | 카드 안 콘텐츠가 경계를 침범한다 | 안쪽 마진 0.20 확보 후 좌표 계산 |
| 10 | 분할 박스 gap이 들쑥날쑥해진다 | 가로 0.20 / 세로 0.15로 고정, padding 0.20을 차감한 뒤 내부 영역을 나눈다 |
| 11 | 저해상도 배경이 픽셀로 깨진다 | 최소 2000×1125, 권장 2400×1350 |
| 12 | 텍스트가 박스 아래로 처져 보인다 | 모든 `addText`에 `valign: "middle"`. 기본값 top은 상단 인셋 + 줄피치 때문에 시각 중심이 무너진다 |
| 13 | 텍스트 박스가 글자보다 훨씬 크면 시각 중심이 어긋난다 | 박스 h를 `줄수 × fontSize / 72 × 1.25` 근처로 맞춘다 |
| 14 | stacked 막대 두 조각 사이에 흰 갭이 생긴다 | `roundRect` 대신 `rect`로 그린다 |
| 15 | 페이지 번호가 PowerPoint에서 다른 서식으로 보인다 | `s.slideNumber` placeholder + 빌드 후 `fix-slidenum.py` 실행 |
| 16 | LibreOffice 렌더에서는 멀쩡한데 PowerPoint에서 글자가 겹치거나 잘린다 | 폰트 메트릭·줄바꿈 계산이 다르다. 최종 확인은 **실제 PowerPoint 렌더**로 한다 |
| 17 | 편집 후 배경 이미지가 사라진다 | pptx를 직접 XML 편집할 때 media 참조가 끊기지 않았는지 확인 후 재렌더 |
| 18 | 문자열 런을 교체하면 줄바꿈(`<a:br>`)이 뭉친다 | 교체 후 br을 다시 삽입하고 PDF로 검증 |

### 이미지·PNG를 섞을 때

- 제목·본문·카드·칩·표·차트·단순 도식은 **pptxgenjs 네이티브 객체**로 만든다. 나중에 파워포인트에서 직접 고칠 수 있어야 한다
- 통짜 슬라이드 PNG를 최종 결과물로 내보내지 않는다. 네이티브로 만들기 어려운 복잡한 시각화만 투명 PNG로 얹는다
- 인포그래픽 안의 라벨은 텍스트 박스로 따로 얹지 말고 이미지에 함께 구워 넣는다. 좌표가 어긋나 겹치기 쉽다
- 삽입 이미지는 통짜 슬라이드 렌더와 별개로 **단독으로 한 번 더 확인**한다

---

## 12. 빌드 후 확인 목록

- [ ] 모든 슬라이드 첫 줄에 배경 이미지, 로고 중복 추가 없음
- [ ] 카드 외곽선 0, 그림자만
- [ ] 모든 `addText`에 `valign: "middle"`
- [ ] 차트 외곽 박스 없음, 축 baseline과 값 grid는 보임
- [ ] 모든 차트에 데이터 라벨
- [ ] 헤더 3요소(`NN · 카테고리` / 26pt 헤드라인 / 12pt 서브타이틀)
- [ ] SO WHAT 띠 풀폭, 가운데 정렬, 위 카드와 gap 0.15
- [ ] 본문 콘텐츠 max y ≤ 6.05
- [ ] 카드 하단 padding 0.18 이상, 위쪽 쏠림 없음
- [ ] stacked 막대 두 조각이 딱 붙음
- [ ] 도넛 hole 안에 수치 + 라벨 두 줄
- [ ] 페이지 번호가 `slideNumber` placeholder, `fix-slidenum.py` 실행함
- [ ] 승인 팔레트 밖 hex 0, 오렌지가 글자에 안 쓰임
- [ ] 줄표·이모지·원형숫자 0
- [ ] 직전 슬라이드와 레이아웃 판이 다름, 시각화 0인 슬라이드 없음
- [ ] Source 표기, 상대 날짜는 절대 날짜로 변환됨
- [ ] `ppt_lint.py` ERROR 0
- [ ] 실제 PowerPoint 렌더로 글자 겹침·잘림 최종 확인
