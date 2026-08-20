@echo off
setlocal

set "PROJECT_NAME=%~1"
if "%PROJECT_NAME%"=="" (
    set /p "PROJECT_NAME=Project folder name: "
)

if "%PROJECT_NAME%"=="" (
    echo Project folder name cannot be empty.
    exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_cad_project.ps1" -ProjectName "%PROJECT_NAME%" -Destination "%CD%"
set "RESULT=%ERRORLEVEL%"

if not "%RESULT%"=="0" (
    echo.
    echo Project setup failed.
    exit /b %RESULT%
)

echo.
echo Project setup completed.
echo Claude and Codex phase prompts are available in prompts\.
endlocal
