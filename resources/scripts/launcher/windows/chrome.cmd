if %PROCESSOR_ARCHITECTURE%==x86 (
"%ProgramFiles%\Google\Chrome\Application\chrome.exe" --start-maximized --disable-translate --disable-new-tab-first-run --no-default-browser-check --no-first-run --kiosk %1
) else (
"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" --start-maximized --disable-translate --disable-new-tab-first-run --no-default-browser-check --no-first-run --kiosk %1
)
