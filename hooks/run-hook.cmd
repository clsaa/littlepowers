: << 'CMDBLOCK'
@echo off
REM Cross-platform launcher for the Littlepowers Python SessionStart hook.
set "HOOK_SCRIPT=%~dp0session-start.py"

where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    py -3 "%HOOK_SCRIPT%"
    exit /b %ERRORLEVEL%
)

where python3 >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python3 "%HOOK_SCRIPT%"
    exit /b %ERRORLEVEL%
)

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python "%HOOK_SCRIPT%"
    exit /b %ERRORLEVEL%
)

REM Missing Python must not prevent the coding session from starting.
>&2 echo littlepowers recovery hook skipped: Python 3 was not found
exit /b 0
CMDBLOCK

#!/usr/bin/env sh
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if command -v python3 >/dev/null 2>&1; then
    exec python3 "${SCRIPT_DIR}/session-start.py"
fi
if command -v python >/dev/null 2>&1; then
    exec python "${SCRIPT_DIR}/session-start.py"
fi

# Missing Python must not prevent the coding session from starting.
echo "littlepowers recovery hook skipped: Python 3 was not found" >&2
exit 0
