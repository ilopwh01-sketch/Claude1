#!/usr/bin/env python3
"""
promote_ppt.py — "합격/확정" 판정을 받은 PPT만 진열장으로 승격한다.

핵심 원칙:
  - 게이트를 통과한 것은 '규칙 위반이 없다'는 뜻일 뿐 '이 안으로 간다'가 아니다.
    통과를 자동 복사 트리거로 걸면 반려본·재빌드 중간산물이 진열장을 오염시킨다.
  - 그래서 승격은 자동이 아니라, 확정 판정이 떨어질 때만 사람이 호출한다.
  - 진열장 파일명은 버전번호를 뺀 '정본명'으로 덮어쓴다. 주제당 항상 최신 1개만 남는다.

사용:
  python3 promote_ppt.py <pptx 경로> "<정본명(확장자 제외)>" [--gallery-dir <폴더>] [--build-source <빌드소스.js|mjs>]

진열장 위치 결정 순서:
  1) --gallery-dir 인자   2) 환경변수 PPT_GALLERY_DIR   3) 현재 폴더의 ./output
  제작자 개인 폴더를 코드에 박으면 남의 컴퓨터에 남의 폴더가 생긴다.

승격 전 lint 강제:
  - 지침 문서는 게이트가 아니다. 관문을 하나로 모으는 것이 실질 방어선이다.
    어느 손으로 만들었든 정본 승격 전 ppt_lint.py를 통과(ERROR 0)해야 한다.
  - 빌드 소스는 build-<pptx이름>.js|mjs를 스크립트 폴더와 pptx 폴더에서 자동 탐색한다.
    이름·위치가 다르면 --build-source로 명시한다. 없으면 승격 중단(fail-closed).
  - 유일한 예외 = PowerPoint로 직접 손수정한 파일(--roji-edited). 사람 손이 최종 권위다.
"""
import sys, os, shutil, hashlib, subprocess
from pathlib import Path
from typing import Optional

DEFAULT_GALLERY = "./output"

def resolve_gallery(cli_dir: Optional[str]) -> Path:
    raw = cli_dir or os.environ.get("PPT_GALLERY_DIR") or DEFAULT_GALLERY
    return Path(raw).expanduser().resolve()

def lint_gate(src: Path, roji_edited: bool, build_source: Optional[Path] = None) -> None:
    """승격 전 ppt_lint ERROR 0 강제. 실패·js부재 = 승격 중단(fail-closed)."""
    if roji_edited:
        print("ℹ️ --roji-edited: 손수정본 — lint 생략(사람 손이 최종 권위).")
        return
    here = Path(__file__).resolve().parent
    candidates = ([build_source] if build_source else [
        here / f"build-{src.stem}.js",
        here / f"build-{src.stem}.mjs",
        src.parent / f"build-{src.stem}.js",
        src.parent / f"build-{src.stem}.mjs",
        src.parent / f"{src.stem}.mjs",
    ])
    js = next((p for p in candidates if p and p.exists()), None)
    if js is None:
        looked = ", ".join(str(p) for p in candidates if p)
        print(f"❌ 승격 중단 — 빌드 스크립트를 못 찾음: {looked}\n"
              f"   어느 손으로 만들었든 승격 전 ppt_lint 통과가 필수다( 관문 단일화).\n"
              f"   외부 빌드는 --build-source <파일.js|mjs>로 지정. 직접 손수정본만 --roji-edited 예외.", file=sys.stderr)
        sys.exit(1)
    # 빈 껍데기 js를 --build-source로 물리면 js 기반 검사(팔레트·시각화)가 공허 통과된다 → 진짜 빌드 스크립트인지 확인
    try:
        _body = js.read_text(encoding="utf-8", errors="ignore")
    except OSError as e:
        print(f"❌ 승격 중단 — 빌드 스크립트를 읽지 못함: {js} ({e})", file=sys.stderr)
        sys.exit(1)
    if ("addText" not in _body) and ("addSlide" not in _body):
        print(f"❌ 승격 중단 — {js.name}에 addText/addSlide가 없음(빌드 스크립트가 아님). "
              f"실제 그 pptx를 만든 빌드 소스를 지정하라.", file=sys.stderr)
        sys.exit(1)
    r = subprocess.run([sys.executable, str(here / "ppt_lint.py"), str(js), str(src)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-2000:], file=sys.stderr)
        print(f"❌ 승격 중단 — ppt_lint ERROR. 0으로 고쳐 다시 빌드 후 승격하라.", file=sys.stderr)
        sys.exit(1)
    print(f"✅ 승격 전 lint 통과 (ppt_lint ERROR 0, {js.name})")

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    args = list(sys.argv[1:])
    roji_edited = "--roji-edited" in args
    args = [a for a in args if a != "--roji-edited"]
    gallery_dir = None
    if "--gallery-dir" in args:
        i = args.index("--gallery-dir")
        if i + 1 >= len(args):
            print("❌ --gallery-dir 뒤에 폴더 경로가 필요함", file=sys.stderr); sys.exit(2)
        gallery_dir = args[i + 1]
        del args[i:i + 2]
    build_source = None
    if "--build-source" in args:
        i = args.index("--build-source")
        if i + 1 >= len(args):
            print("❌ --build-source 뒤에 파일 경로가 필요함", file=sys.stderr); sys.exit(2)
        build_source = Path(args[i + 1]).expanduser().resolve()
        del args[i:i + 2]
    if len(args) != 2:
        print("사용법: promote_ppt.py <src.pptx> \"<슬라이드 정본명>\" "
              "[--gallery-dir <폴더>] [--build-source <빌드소스.js|mjs>] [--roji-edited]", file=sys.stderr)
        sys.exit(2)
    DEST = resolve_gallery(gallery_dir)
    src = Path(args[0]).expanduser()
    if not src.is_absolute():
        # 상대경로는 실행한 폴더 기준이 먼저다. 스크립트 폴더 기준으로만 찾으면
        # README대로 번들 루트에서 `python3 scripts/promote_ppt.py v02.pptx` 했을 때
        # scripts/ 안을 뒤지다 "원본 없음"으로 죽는다 ).
        _cands = [Path.cwd() / src, Path(__file__).resolve().parent / src]
        src = next((c for c in _cands if c.exists()), _cands[0])
    canonical = args[1].strip()
    if not src.exists():
        print(f"❌ 원본 없음: {src}", file=sys.stderr)
        sys.exit(1)
    lint_gate(src, roji_edited, build_source)
    # 정본명 방어(외부 검증): basename만 허용 — /·.. 로 목적지 폴더를 못 벗어나게
    if (not canonical or canonical.startswith("~$")
            or "/" in canonical or "\\" in canonical or canonical.startswith(".")
            or Path(canonical).name != canonical):
        print(f"❌ 정본명이 이상함(경로문자·상위이동 금지): {canonical!r}", file=sys.stderr)
        sys.exit(1)
    DEST.mkdir(parents=True, exist_ok=True)
    dst = DEST / f"{canonical}.pptx"
    existed = dst.exists()

    # 원자적 교체(외부 검증): 임시파일에 복사 → 해시 확인 → os.replace.
    # 검증 통과 전엔 기존 정본을 절대 안 건드린다(손상본 남기지 않음).
    tmp = DEST / f".{canonical}.pptx.tmp"
    shutil.copy2(src, tmp)
    src_hash, tmp_hash = sha256(src), sha256(tmp)
    if src_hash != tmp_hash:
        tmp.unlink(missing_ok=True)
        print(f"❌ 승격 실패 — 해시 불일치(복사 손상), 기존 정본 보존\n   원본 {src_hash}\n   사본 {tmp_hash}", file=sys.stderr)
        sys.exit(1)
    os.replace(tmp, dst)  # 같은 볼륨 → 원자적
    dst_hash = tmp_hash

    # 잠금 찌꺼기(~$*.pptx)는 자동삭제 금지 — 열려 있는 정상 PPT의 활성 잠금일 수 있어 경고만
    junk = list(DEST.glob("~$*.pptx"))
    if junk:
        names = ", ".join(j.name for j in junk)
        print(f"⚠️ 진열장에 PowerPoint 잠금 찌꺼기 있음(자동삭제 안 함 — 열린 파일일 수 있음): {names}")

    verb = "덮어씀(최신 정본 교체)" if existed else "새로 진열"
    print(f"✅ 진열장 승격 완료 — {verb}\n   {dst}\n   해시검증 OK: {dst_hash[:16]}…")

if __name__ == "__main__":
    main()
