//============================================================================
//페이퍼로지 PPT 표준 템플릿 (Paperlogy PPT Standard Template : locked)
//============================================================================
//확정된 표준 디자인 그대로다. 좌표·색·폰트 사양은 바꾸지 않는다.
//새 PPT 빌드 시 무조건 이 파일 복사 → 데이터·문구만 교체. 디자인 사양 임의 변경 금지.
////디자인 사양 전체 명세: DESIGN-SYSTEM.md
//검사 규칙 전수:        GATES.md
////표준 사양 요약:
//- 배경: assets/Background_paperlogy.jpg 전 슬라이드
//- 카드: 흰 박스 line none + shadow만 / radius 0.18
//- 위 박스 사이즈: 좌 (0.422, 2.20, 7.95, 3.85) · 우 (8.567, 2.20, 4.345, 3.85)
//- 차트 라인: 외곽 박스·grid·tick X / 축 baseline AXIS_GREY·값 grid GRID_GREY
//- SO WHAT 박스: x 0.422, y 6.20, w 12.49, h 0.40 (위 박스 끝 6.05와 gap 0.15)
//- 헤더 chapter: "NN · 카테고리" / headline 26pt bold / subtitle 12pt
//- 인사이트 카드: KEY INSIGHT 라벨 + 거대 숫자 + 미니 비교 막대 + 칩 2개
//- KPI 칩 카드: 큰 배수 + 라벨 + stacked 막대 (rect, 라운드 X : 두 막대 딱 붙음)
//- 도넛 hole: 점유 % + 라벨 두 줄
////memory: paperlogy-ppt-strict-design

const pptxgen = require("pptxgenjs");
const pres = new pptxgen();

pres.defineLayout({ name: "BRANDLOGY_169", width: 13.333, height: 7.5 });
pres.layout = "BRANDLOGY_169";
pres.title = "샘플 발표자료 v01";

const FONT = "Pretendard";
const FONT_M = "Pretendard Medium";
const C = {
  //표준 블루 = 클라인 블루 ) · 메모리 paperlogy-ppt-strict-design
  brand: "002FA7", brandDeep: "001C64", accent: "FF7A00",
  brandT2: "4D6DC1", brandT3: "99ACDB", brandT4: "D9E0F2",
  brandPale: "EAEEF8",
  ink: "222222", text: "3A4654", mute: "5A6678",
  caption: "8A94A2", source: "5F6B78",
  white: "FFFFFF", surface2: "EFF2F6", surface3: "F4F6F9",
};

const sContainer = () => ({ type: "outer", color: "000000", blur: 12, offset: 2, angle: 90, opacity: 0.05 });

const BG_PATH = require("path").join(__dirname, "assets", "Background_paperlogy.jpg");
function addBackground(s) {
  s.addImage({ path: BG_PATH, x: 0, y: 0, w: 13.333, h: 7.5 });
}

function addHeader(s, chapter, headline, subtitle) {
  s.addText(chapter, {
    x: 0.422, y: 0.306, w: 8, h: 0.3,
    fontFace: FONT, fontSize: 10, bold: true, color: C.brand, charSpacing: 2, valign: "middle" });
  s.addText(/[.?!]$/.test(headline) ? headline : headline + ".", {  //대제목 마침표 필수 ()
    x: 0.422, y: 0.851, w: 12.262, h: 0.55,
    fontFace: FONT, fontSize: 26, bold: true, color: C.ink, valign: "middle"});
  if (subtitle) {
    s.addText(subtitle, {
      x: 0.422, y: 1.472, w: 12.262, h: 0.303,
      fontFace: FONT, fontSize: 12, color: C.text, valign: "middle" });
  }
}

function box(s, x, y, w, h, o = {}) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h,
    fill: { color: o.fill || C.white },
    line: { type: "none" },
    rectRadius: o.r || 0.18,
    shadow: o.shadow !== false ? sContainer() : undefined
  });
}

// SO WHAT 박스: 위 흰 박스(끝 5.75)와 gap 0.45 확보
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
    align: "center", valign: "middle"});
}

function addBottomStrip(s, pageNum, source) {
  s.addText(source, {
    x: 0.535, y: 6.85, w: 11, h: 0.3,
    fontFace: FONT, fontSize: 8, color: C.source, valign: "middle" });
  // 페이지 번호 = PowerPoint 네이티브 자동 슬라이드 번호(placeholder).
  //고정 텍스트 X : 슬라이드를 다른 PPT에 붙여넣으면 위치에 맞게 자동 갱신됨.
  //pageNum 인자는 기존 호출부 호환 위해 받되 미사용.
  s.slideNumber = {
    x: 12.45, y: 6.85, w: 0.5, h: 0.3,
    fontFace: FONT, fontSize: 8, color: C.caption, align: "right"};
}

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

//=====================================================================
//SLIDE 1 : 부문별 채널 매출 비교 (Group Bar)
//=====================================================================
const s2 = pres.addSlide();
addBackground(s2);
addHeader(s2,
  "01 · 부문별 채널 매출",
  "식품·뷰티·리빙은 온라인, 의류·가전은 오프라인 우위",
  "5개 부문 채널별 매출 비교 (가상 예시 데이터, 단위 십억 USD)"
);

box(s2, 0.422, 2.20, 7.95, 3.85);
box(s2, 8.567, 2.20, 4.345, 3.85);

s2.addChart(pres.charts.BAR, [
  {
    name: "오프라인",
    labels: ["가전", "의류", "식품", "뷰티", "리빙"],
    values: [18, 25, 8, 2, 1]
  },
  {
    name: "온라인",
    labels: ["가전", "의류", "식품", "뷰티", "리빙"],
    values: [2, 8, 10, 6, 3]
  }
], {
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

//─── 우측 인사이트 카드 (재디자인) ────────────────────────────
const CX = 8.567;       //카드 좌측 x
const CW = 4.345;       //카드 폭
const PAD = 0.30;       //내부 좌우 패딩
const ix = CX + PAD;    //내부 컨텐츠 x
const iw = CW - PAD * 2;//내부 컨텐츠 w

//(1) 라벨
s2.addText("KEY INSIGHT", {
  x: ix, y: 2.40, w: iw, h: 0.28,
  fontFace: FONT, fontSize: 9, bold: true, color: C.brand,
  charSpacing: 3, align: "left", valign: "middle" });

//(2) 거대 숫자 : 온라인 전체 매출
s2.addText("29B", {
  x: ix, y: 2.70, w: iw, h: 1.05,
  fontFace: FONT, fontSize: 56, bold: true, color: C.brandDeep,
  align: "left", valign: "middle", charSpacing: -1
});

//(3) 한 줄 설명
s2.addText("온라인 5개 부문 매출 합 (USD)", {
  x: ix, y: 3.78, w: iw, h: 0.28,
  fontFace: FONT, fontSize: 11, color: C.mute, align: "left", valign: "middle" });

//(4) 미니 비교 막대 : 전체 매출 온라인 vs 오프라인 (max 60B 기준)
const barY = 4.15;
const barH = 0.22;
const labelW = 0.78;
const valW = 0.65;
const trackX = ix + labelW;
const trackW = iw - labelW - valW - 0.08;
const ON_PCT = 48, OFF_PCT = 90;   //온라인 29B / 오프라인 54B (max 60B 기준 %)

//온라인 라벨
s2.addText("온라인", {
  x: ix, y: barY, w: labelW, h: barH,
  fontFace: FONT_M, fontSize: 10, color: C.ink, valign: "middle"
});
//온라인 트랙 (옅은 회색)
s2.addShape(pres.ShapeType.roundRect, {
  x: trackX, y: barY + 0.06, w: trackW, h: 0.10,
  fill: { color: "EEF0F4" }, line: { type: "none" }, rectRadius: 0.05
});
//온라인 값 막대 (brand)
s2.addShape(pres.ShapeType.roundRect, {
  x: trackX, y: barY + 0.06, w: trackW * (ON_PCT / 100), h: 0.10,
  fill: { color: C.brand }, line: { type: "none" }, rectRadius: 0.05
});
s2.addText("29B", {
  x: trackX + trackW + 0.05, y: barY, w: valW, h: barH,
  fontFace: FONT, fontSize: 10, bold: true, color: C.brandDeep, valign: "middle"
});

//오프라인 라벨
const barY2 = barY + 0.40;
s2.addText("오프라인", {
  x: ix, y: barY2, w: labelW, h: barH,
  fontFace: FONT_M, fontSize: 10, color: C.mute, valign: "middle"
});
s2.addShape(pres.ShapeType.roundRect, {
  x: trackX, y: barY2 + 0.06, w: trackW, h: 0.10,
  fill: { color: "EEF0F4" }, line: { type: "none" }, rectRadius: 0.05
});
s2.addShape(pres.ShapeType.roundRect, {
  x: trackX, y: barY2 + 0.06, w: trackW * (OFF_PCT / 100), h: 0.10,
  fill: { color: C.mute }, line: { type: "none" }, rectRadius: 0.05
});
s2.addText("54B", {
  x: trackX + trackW + 0.05, y: barY2, w: valW, h: barH,
  fontFace: FONT, fontSize: 10, bold: true, color: C.mute, valign: "middle"
});

//(5) 구분선
s2.addShape(pres.ShapeType.line, {
  x: ix, y: 5.10, w: iw, h: 0,
  line: { color: "EEF0F4", width: 1 }
});

//(6) 보조 KPI 칩 2개
const chipY = 5.25;
const chipH = 0.55;
const chipGap = 0.10;
const chipW = (iw - chipGap) / 2;

//칩 1 : 온라인 우위 부문
s2.addShape(pres.ShapeType.roundRect, {
  x: ix, y: chipY, w: chipW, h: chipH,
  fill: { color: "F6F7FB" }, line: { type: "none" }, rectRadius: 0.06
});
s2.addText("온라인 우위 부문", {
  x: ix + 0.10, y: chipY + 0.04, w: chipW - 0.20, h: 0.20,
  fontFace: FONT, fontSize: 8, color: C.mute, charSpacing: 1, valign: "middle" });
s2.addText("3개", {
  x: ix + 0.10, y: chipY + 0.22, w: chipW - 0.20, h: 0.30,
  fontFace: FONT, fontSize: 16, bold: true, color: C.brand, valign: "middle" });

//칩 2 : 오프라인 우위 부문
const chip2X = ix + chipW + chipGap;
s2.addShape(pres.ShapeType.roundRect, {
  x: chip2X, y: chipY, w: chipW, h: chipH,
  fill: { color: "F6F7FB" }, line: { type: "none" }, rectRadius: 0.06
});
s2.addText("오프라인 우위 부문", {
  x: chip2X + 0.10, y: chipY + 0.04, w: chipW - 0.20, h: 0.20,
  fontFace: FONT, fontSize: 8, color: C.mute, charSpacing: 1, valign: "middle" });
s2.addText("2개", {
  x: chip2X + 0.10, y: chipY + 0.22, w: chipW - 0.20, h: 0.30,
  fontFace: FONT, fontSize: 16, bold: true, color: C.brand, valign: "middle" });

addSoWhat(s2, "오프라인은 대형 부문 강자, 온라인은 성장 부문 강자. 서로 보완하는 구조입니다.");
addBottomStrip(s2, 1, "Source: 스킬 예시용 가상 데이터 (실제 통계가 아닙니다, 단위: 십억 USD)");

//=====================================================================
//SLIDE 3 : 부문별 채널 점유 (Doughnut x2 + KPI)
//=====================================================================
const s3 = pres.addSlide();
addBackground(s3);
addHeader(s3,
  "02 · 부문별 채널 점유",
  "식품·뷰티는 온라인, 의류·가전은 오프라인이 결정적 우위",
  "격차가 큰 4개 부문, 두 채널 합산 100% 기준 점유율"
);

box(s3, 0.422, 2.20, 7.95, 3.85);
box(s3, 8.567, 2.20, 4.345, 3.85);

//─── 좌측 카드 : 도넛 hole에 [점유 % + 라벨] ───────────
s3.addText("COMPARISON", {
  x: 0.66, y: 2.34, w: 5, h: 0.22,
  fontFace: FONT, fontSize: 9, bold: true, color: C.brand, charSpacing: 3, valign: "middle" });
s3.addText("식품은 온라인 우세, 의류는 오프라인 압도", {
  x: 0.66, y: 2.56, w: 7.5, h: 0.30,
  fontFace: FONT, fontSize: 13, bold: true, color: C.ink, valign: "middle" });

//도넛 2개 (상단 title 제거, hole 안 두 줄로 정보 박음)
const dy = 2.95, dw = 3.50, dh = 2.20;
const dx1 = 0.55, dx2 = 4.20;

//도넛 1 : 식품 점유율 (온라인 우위, 온 10 / 오프 8 = 56% / 44%)
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
//도넛 1 hole 안 : 온라인 점유 + 라벨
s3.addText("식품", {
  x: dx1 + 0.3, y: dy + dh / 2 - 0.26, w: dw - 0.6, h: 0.30,
  fontFace: FONT, fontSize: 15, bold: true, color: C.brandDeep,
  align: "center", valign: "middle"
});
s3.addText("온라인 우세", {
  x: dx1 + 0.3, y: dy + dh / 2 + 0.04, w: dw - 0.6, h: 0.22,
  fontFace: FONT, fontSize: 9, color: C.mute,
  align: "center", valign: "middle", charSpacing: 1
});

//도넛 2 : 의류 점유율 (오프라인 압도, 온 8 / 오프 25 = 24% / 76%)
s3.addChart(pres.charts.DOUGHNUT, [
  { name: "의류 점유", labels: ["오프라인", "온라인"], values: [76, 24] }
], {
  x: dx2, y: dy, w: dw, h: dh,
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
s3.addText("의류", {
  x: dx2 + 0.3, y: dy + dh / 2 - 0.26, w: dw - 0.6, h: 0.30,
  fontFace: FONT, fontSize: 15, bold: true, color: C.brandDeep,
  align: "center", valign: "middle"
});
s3.addText("오프라인 우세", {
  x: dx2 + 0.3, y: dy + dh / 2 + 0.04, w: dw - 0.6, h: 0.22,
  fontFace: FONT, fontSize: 9, color: C.mute,
  align: "center", valign: "middle", charSpacing: 1
});

//도넛 하단 부가 한 줄 : 채널별 수치 (가운데)
s3.addText("온 10B · 오프 8B", {
  x: dx1, y: dy + dh + 0.05, w: dw, h: 0.22,
  fontFace: FONT_M, fontSize: 10, color: C.text, align: "center", valign: "middle" });
s3.addText("온 8B · 오프 25B", {
  x: dx2, y: dy + dh + 0.05, w: dw, h: 0.22,
  fontFace: FONT_M, fontSize: 10, color: C.text, align: "center", valign: "middle" });

//하단 범례 (카드 가운데) : 박스 끝(6.05)에서 여백 0.30 확보
const legY = 5.50;
const legW = 1.40;
const legGap = 0.20;
const legCenter = 0.422 + 7.95 / 2;
const legStartX = legCenter - (legW * 2 + legGap) / 2;
s3.addShape(pres.ShapeType.rect, {
  x: legStartX, y: legY + 0.06, w: 0.18, h: 0.18,
  fill: { color: C.mute }, line: { type: "none" }
});
s3.addText("오프라인", {
  x: legStartX + 0.25, y: legY, w: 0.8, h: 0.30,
  fontFace: FONT, fontSize: 10, color: C.text, valign: "middle"
});
s3.addShape(pres.ShapeType.rect, {
  x: legStartX + legW + legGap, y: legY + 0.06, w: 0.18, h: 0.18,
  fill: { color: C.brand }, line: { type: "none" }
});
s3.addText("온라인", {
  x: legStartX + legW + legGap + 0.25, y: legY, w: 0.7, h: 0.30,
  fontFace: FONT, fontSize: 10, color: C.text, valign: "middle"
});

//─── 우측 KPI 카드 재디자인 : 4 KPI 칩 카드 ────────────────
//상단 라벨 + 미니 헤드
s3.addText("KEY INDICATORS", {
  x: 8.77, y: 2.34, w: 4, h: 0.22,
  fontFace: FONT, fontSize: 9, bold: true, color: C.brand, charSpacing: 3, valign: "middle" });
s3.addText("부문별 채널 우위 정리", {
  x: 8.77, y: 2.56, w: 4, h: 0.30,
  fontFace: FONT, fontSize: 13, bold: true, color: C.ink, valign: "middle" });

//부문별 (각 부문 두 채널 합산 100% 기준 온라인 점유 / 오프라인 점유)
//주의: 순서·구성은 헤드라인이 지목한 부문·순서와 일치시킨다 (식품·뷰티 → 의류·가전).
//   도넛(식품·의류)과도 같은 집합이어야 한 슬라이드 안에서 논리가 어긋나지 않는다.
const kpis = [
  { val: "1.3×", lbl: "식품 (온↑)",   onPct: 56, offPct: 44, onAbs: "10B",  offAbs: "8B"},
  { val: "3.0×", lbl: "뷰티 (온↑)",   onPct: 75, offPct: 25, onAbs: "6B",   offAbs: "2B"},
  { val: "3.1×", lbl: "의류 (오프↑)", onPct: 24, offPct: 76, onAbs: "8B",   offAbs: "25B"},
  { val: "9.0×", lbl: "가전 (오프↑)", onPct: 10, offPct: 90, onAbs: "2B",   offAbs: "18B" }
];

const kpiX = 8.77;
const kpiW = 4.00;
const kpiH = 0.66;
const kpiGap = 0.08;
const kpiStartY = 3.00;

kpis.forEach((k, i) => {
  const ky = kpiStartY + i * (kpiH + kpiGap);

  //카드 fill (옅은 회색)
  s3.addShape(pres.ShapeType.roundRect, {
    x: kpiX, y: ky, w: kpiW, h: kpiH,
    fill: { color: "F6F7FB" }, line: { type: "none" }, rectRadius: 0.08
  });

  //좌측: 큰 배수
  s3.addText(k.val, {
    x: kpiX + 0.20, y: ky, w: 1.05, h: kpiH,
    fontFace: FONT, fontSize: 22, bold: true, color: C.brandDeep,
    align: "left", valign: "middle"});

  //세로 구분선
  s3.addShape(pres.ShapeType.line, {
    x: kpiX + 1.32, y: ky + 0.14, w: 0, h: kpiH - 0.28,
    line: { color: "DDE1E8", width: 0.75 }
  });

  //우측: 라벨 (위) + stacked 비교 막대 (아래)
  s3.addText(k.lbl, {
    x: kpiX + 1.45, y: ky + 0.08, w: 2.40, h: 0.22,
    fontFace: FONT_M, fontSize: 10, color: C.ink,
    align: "left", valign: "middle"});

  //비교 막대 : stacked (온라인 brand + 오프라인 mute)
  const barX = kpiX + 1.45;
  const barY = ky + 0.34;
  const barW = 2.30;
  const barInnerH = 0.12;
  const krW = barW * (k.onPct / 100);
  const jpW = barW * (k.offPct / 100);

  //stacked : 두 조각 딱 붙게 rect로 (라운드 제거)
  s3.addShape(pres.ShapeType.rect, {
    x: barX, y: barY, w: krW, h: barInnerH,
    fill: { color: C.brand }, line: { type: "none" }
  });
  s3.addShape(pres.ShapeType.rect, {
    x: barX + krW, y: barY, w: jpW, h: barInnerH,
    fill: { color: C.mute }, line: { type: "none" }
  });

  //막대 아래 채널별 절댓값 (작게)
  s3.addText([
    { text: "온 ", options: { color: C.brand, fontSize: 8, bold: true } },
    { text: k.onAbs, options: { color: C.ink, fontSize: 8, bold: true } },
    { text: "·   ", options: { color: C.caption, fontSize: 8 } },
    { text: "오프 ", options: { color: C.mute, fontSize: 8, bold: true } },
    { text: k.offAbs, options: { color: C.mute, fontSize: 8, bold: true } }
  ], {
    x: barX, y: barY + barInnerH + 0.02, w: barW, h: 0.18,
    fontFace: FONT, align: "left", valign: "middle"});
});

addSoWhat(s3, "두 채널 모두 주력 부문이 있고, 겹치는 영역만 다릅니다.");
addBottomStrip(s3, 2, "Source: 스킬 예시용 가상 데이터 / 두 채널 합산 100% 기준 점유율 계산 (단위: 십억 USD)");

//=====================================================================
// 출력 후 반드시 fix-slidenum.py 로 자동 슬라이드 번호 fld에 서식 주입
//   (PowerPoint가 마스터 기본 서식으로 덮지 못하게 : 기존 번호와 100% 동일 디자인)
pres.writeFile({ fileName: "샘플-발표자료-v01.pptx" })
  .then((fn) => {
    const _cp = require("child_process"), _p = require("path");
    _cp.execSync(`python3 "${_p.join(__dirname, "fix-slidenum.py")}" "${fn}"`, { stdio: "inherit" });
    // 코드 강제: 빌드 끝에 ppt_lint 자동 검사 (줄표·이모지·원형숫자·자동번호·배경). ERROR 0 전엔 완료 보고 금지.
    //)를 삼키고 ' 빌드 완료'를 찍어, node 직접 빌드 시
    //  게이트가 무력화됐다. → ERROR면 process.exit(1)로 실제로 빌드를 실패시킨다(완료 보고 차단).
    try { _cp.execSync(`python3 "${_p.join(__dirname, "ppt_lint.py")}" "${__filename}" "${fn}"`, { stdio: "inherit" }); }
    catch (e) { console.log(" ppt_lint ERROR : 위 목록을 0으로 고쳐 다시 빌드할 것. ERROR 있는 채로 '완료' 보고 금지."); process.exit(1); }
    console.log(` 빌드 완료: ${fn}`);
  })
  .catch((err) => { console.error(" 빌드 실패:", err); process.exit(1); });
