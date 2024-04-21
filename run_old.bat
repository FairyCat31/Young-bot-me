@echo off
:frestart2
call env/Scripts/activate
cd app/
:restart
py scripts/update.py
if %ERRORLEVEL%==1 goto end
if %ERRORLEVEL%==2 goto restart
if %ERRORLEVEL%==3 goto frestart
py scripts/main.py -name ElderMouse
goto end
:frestart
cd ..
goto frestart2
:end
pause
