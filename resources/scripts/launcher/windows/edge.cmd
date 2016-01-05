@ECHO OFF
TASKKILL /im MicrosoftEdge.exe

start microsoft-edge:%1
%~dp0\..\..\keysender\windows\edge.cmd maximize

:LOOP
TASKLIST | FIND /I "MicrosoftEdge.exe" >nul 2>&1
IF ERRORLEVEL 1 (
  GOTO CONTINUE
) ELSE (
  Timeout /T 2 /Nobreak
  GOTO LOOP
)

:CONTINUE
