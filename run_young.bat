@echo off
:frestart2
call env/Scripts/activate
cd app/
:restart
python scripts/update.py
cls
if %ERRORLEVEL%==1 goto end
if %ERRORLEVEL%==2 goto restart
if %ERRORLEVEL%==3 goto frestart
python scripts/main.py -name_bot YoungMouse
goto end
:frestart
cd ..
goto frestart2
:end
pause
