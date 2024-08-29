@echo off
echo Listing recent critical events...

rem Get a list of recent critical events
for /f "skip=1 tokens=1,2,3,4 delims=," %%a in ('wevtutil qe System /q:*[System[(Level=1)]] /rd:true /f:csv /c:1') do (
  rem Print the details of the current event
  echo.
  echo Date: %%a
  echo Time: %%b
  echo Event ID: %%c
  echo Description: %%d
)

echo Done.

