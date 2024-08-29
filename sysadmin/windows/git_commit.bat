@echo off
setlocal enabledelayedexpansion

set "tempFile=%temp%\commit_message.txt"

echo Please enter commit message. Press Ctrl+Z and Enter to finish:
more > "%tempFile%"

set "multiLineInput="
for /f "delims=" %%i in (%tempFile%) do (
    set "multiLineInput=!multiLineInput!%%i\n"
)

echo Git message:
echo.
echo !multiLineInput!

git add .

git commit -F "%tempFile%"

git push

del "%tempFile%"

endlocal
pause
