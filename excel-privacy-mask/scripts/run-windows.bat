@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
cd /d "%~dp0"
cls
echo ──────────────────────────────────────────
echo   엑셀 개인정보 마스킹
echo ──────────────────────────────────────────
echo.
echo   AI에 넣기 전에 개인정보를 자동으로 가립니다.
echo    · 이름·전화·이메일  -^>  번호로 치환
echo    · 주민번호·계좌·카드  -^>  컬럼 삭제
echo    · 생년월일 -^> 연령대 / 주소 -^> 시·구까지
echo.
echo   ※ 알려진 개인정보 패턴이 남으면 파일을 만들지 않고 멈춥니다.
echo.
echo ──────────────────────────────────────────
echo.
echo   엑셀 파일을 이 창에 끌어다 놓고 엔터를 누르세요.
echo.
set /p FILEPATH="  파일: "
set FILEPATH=%FILEPATH:"=%

if not exist "%FILEPATH%" (
  echo.
  echo   [X] 파일을 찾을 수 없습니다: %FILEPATH%
  echo.
  pause
  exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
  echo.
  echo   [X] 파이썬이 설치돼 있지 않습니다.
  echo       https://www.python.org/downloads/ 에서 설치할 때
  echo       "Add python.exe to PATH" 를 반드시 체크하세요.
  echo.
  pause
  exit /b 1
)

python -c "import openpyxl" >nul 2>&1
if errorlevel 1 (
  echo.
  echo   처음 실행이라 필요한 도구를 설치합니다 ^(1회, 약 10초^)...
  python -m pip install --quiet openpyxl
)

echo.
set "LOGFILE=%TEMP%\excel_privacy_mask_%RANDOM%_%RANDOM%.log"
python "%~dp0..\mask_excel.py" "%FILEPATH%" > "%LOGFILE%" 2>&1
set STATUS=%errorlevel%
type "%LOGFILE%"
echo.
if %STATUS%==0 (
  set "MASKED_PATH="
  for /f "tokens=1,* delims=:" %%A in ('findstr /b /c:"마스킹:" "%LOGFILE%"') do set "MASKED_PATH=%%B"
  if defined MASKED_PATH set "MASKED_PATH=!MASKED_PATH:~1!"
  echo   새로 만든 마스킹 파일을 선택해서 보여드립니다.
  if defined MASKED_PATH (
    explorer /select,"!MASKED_PATH!"
  ) else (
    for %%F in ("%FILEPATH%") do explorer "%%~dpF"
  )
) else (
  echo   [!] 개인정보가 남아 있어 파일을 만들지 않았습니다. 위 내용을 확인하세요.
)
del "%LOGFILE%" >nul 2>&1
echo.
pause
