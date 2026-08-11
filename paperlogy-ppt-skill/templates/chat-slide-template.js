//템플릿 : 채팅 화면이 주인공인 슬라이드 (1 slide). 대화 내용·인물은 각자 것으로 교체한다.
//디자인 예외: 우측 키포인트 없음, 채팅창(claude.ai UI)이 주인공. 대화 16턴(좌 1~8 → 우 9~16, 2단).
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.defineLayout({ name: "BRANDLOGY_169", width: 13.333, height: 7.5 });
pres.layout = "BRANDLOGY_169";
pres.title = "Chat Slide";
const FONT = "Pretendard";
const C = {
  brand: "002FA7", brandDeep: "001C64", brandT2: "4D6DC1", brandT3: "99ACDB",
  brandT4: "D9E0F2", brandPale: "EAEEF8",
  ink: "222222", text: "404040", mute: "45515E", caption: "8E8E93", source: "5F5F5F",
  white: "FFFFFF", surface2: "F0F0F0", surface3: "F2F3F5", border: "E5E7EB",
};
const sContainer = () => ({ type: "outer", color: "000000", blur: 9, offset: 1.2, angle: 90, opacity: 0.05 });
const BG_PATH = require("path").join(__dirname, "assets", "Background_paperlogy.jpg");
function addBackground(s) { s.addImage({ path: BG_PATH, x: 0, y: 0, w: 13.333, h: 7.5 }); }
function addHeader(s, chapter, headline) {
  s.addText(chapter, { x: 0.422, y: 0.30, w: 12, h: 0.3, fontFace: FONT, fontSize: 10, bold: true, color: C.brand, charSpacing: 2, valign: "middle" });
  s.addText(headline, { x: 0.422, y: 0.80, w: 12.262, h: 0.55, fontFace: FONT, fontSize: 24, bold: true, color: C.ink, valign: "middle" });
}
function addSoWhat(s, msg) {
  s.addShape(pres.ShapeType.roundRect, { x: 0.422, y: 6.20, w: 12.49, h: 0.40, fill: { color: C.surface2 }, line: { type: "none" }, rectRadius: 0.06 });
  s.addText([
    { text: "SO WHAT", options: { bold: true, color: C.brand, fontSize: 10, charSpacing: 2 } },
    { text: "     " }, { text: msg, options: { color: C.ink, fontSize: 11 } }
  ], { x: 0.422, y: 6.20, w: 12.49, h: 0.40, fontFace: FONT, align: "center", valign: "middle" });
}
function addBottomStrip(s, source) {
  s.addText(source, { x: 0.535, y: 6.85, w: 11, h: 0.3, fontFace: FONT, fontSize: 8, color: C.source, valign: "middle" });
  s.slideNumber = { x: 12.45, y: 6.85, w: 0.5, h: 0.3, fontFace: FONT, fontSize: 8, color: C.caption, align: "right" };
}
//채팅 말풍선 : 나(컬럼 우측·주황) / Claude(컬럼 좌측·흰), 컬럼 내 가변 폭
function bubble(s, who, text, y, cL, cR) {
  const mine = who === "나", H = 0.38;
  const len = [...text].length;
  const w = Math.min(cR - cL, len * 0.125 + 0.42);
  const bx = mine ? cR - w : cL;
  s.addShape(pres.ShapeType.roundRect, { x: bx, y: y, w: w, h: H, fill: { color: mine ? C.brand : C.white }, line: mine ? { type: "none" } : { color: C.border, width: 1 }, rectRadius: 0.10, shadow: sContainer() });
  s.addText(text, { x: bx + 0.14, y: y, w: w - 0.28, h: H, fontFace: FONT, fontSize: 9.5, color: mine ? C.white : C.ink, valign: "middle" });
}

{
  const s = pres.addSlide();
  addBackground(s);
  addHeader(s, "01 · 첫 마디 (The Prompt)",
    "이렇게 채팅을 칩니다 : ‘아침 비서’이 태어난 대화");

  //채팅 컨테이너 (claude.ai 창)
  s.addShape(pres.ShapeType.roundRect, { x: 0.422, y: 1.56, w: 12.49, h: 4.5, fill: { color: C.white }, line: { type: "none" }, rectRadius: 0.10, shadow: sContainer() });
  s.addText([
    { text: "Claude   ", options: { bold: true, color: C.brand, fontSize: 11.5 } },
    { text: "아침 비서이 된 첫 대화", options: { color: C.caption, fontSize: 9.5 } },
  ], { x: 0.75, y: 1.66, w: 11, h: 0.28, fontFace: FONT, valign: "middle" });
  s.addShape(pres.ShapeType.line, { x: 0.7, y: 1.98, w: 11.93, h: 0, line: { color: C.border, width: 0.75 } });
  //좌·우 2단 구분선 + 흐름 표시
  s.addShape(pres.ShapeType.line, { x: 6.66, y: 2.12, w: 0, h: 3.74, line: { color: C.border, width: 0.75 } });

  const L = [
    ["나", "매일 아침 메일·일정 챙기는 데 30분씩 써."],
    ["Claude", "‘브리핑’ 하시면 한 화면에 묶어 드려요."],
    ["나", "답장 안 한 메일부터. 보낸이·요지·날짜로."],
    ["Claude", "돈 관련 메일도 같이 넣을까요?"],
    ["나", "아니, 돈은 빼. 그건 따로 볼게."],
    ["Claude", "회신 초안도 미리 뽑아둘까요?"],
    ["나", "응, 답장은 무조건 전체회신으로."],
    ["Claude", "전체회신 기본으로 고정할게요."],
  ];
  const R = [
    ["나", "일정도 챙겨줘. 강의·미팅 안 헷갈리게."],
    ["Claude", "[강의]·[미팅]로 분류, 강의는 2시간 기본으로."],
    ["나", "겹치는 일정 있으면 미리 알려줘."],
    ["Claude", "충돌 나면 짚고 재배치안까지 드려요."],
    ["나", "새 할 일은 노션 보드에 정리해줘."],
    ["Claude", "노션 할 일 보드에 카드로 추가할게요."],
    ["나", "좋아. 이 방식 기억해 : ‘아침 비서’이야."],
    ["Claude", "고정 완료. ‘브리핑’이면 다 정리해요."],
  ];
  let y = 2.16;
  L.forEach(([w, t]) => { bubble(s, w, t, y, 0.72, 6.18); y += 0.46; });
  y = 2.16;
  R.forEach(([w, t]) => { bubble(s, w, t, y, 6.92, 12.18); y += 0.46; });

  addSoWhat(s, "이 한 번의 대화가 그대로 ‘아침 비서’ 지침이 됐어요 : 막연한 고민을 풀고, 원칙을 하나씩 얹은 게 전부입니다.");
  addBottomStrip(s, "Source: 페이퍼로지 : 아침 비서 지침이 만들어진 흐름을 재구성");
}

const path = require("path");
const OUT = path.join(__dirname, "샘플-채팅슬라이드-v01.pptx");
pres.writeFile({ fileName: OUT }).then(p => {
  require("child_process").execSync(`python3 "${path.join(__dirname, "fix-slidenum.py")}" "${OUT}"`, { stdio: "inherit" });
  try { require("child_process").execSync(`python3 "${path.join(__dirname, "ppt_lint.py")}" "${__filename}" "${OUT}"`, { stdio: "inherit" }); }
  catch (e) { console.log(" ppt_lint ERROR : 위 목록을 0으로 고쳐 다시 빌드. ERROR 있는 채 '완료' 금지."); }
  console.log(" Saved:", p);
}).catch(e => { console.error("", e); process.exit(1); });
