@ECHO OFF
TASKKILL /im iexplore.exe

"%ProgramFiles%\Internet Explorer\iexplore.exe" -noframemerging -k %1

:LOOP
TASKLIST | FIND /I "iexplore.exe" >nul 2>&1
IF ERRORLEVEL 1 (
  GOTO CONTINUE
) ELSE (
  Timeout /T 2 /Nobreak
  GOTO LOOP
)

:CONTINUE
