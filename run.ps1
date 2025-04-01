env/Scripts/activate.ps1
$env:PYTHONPATH = $PWD.Path

python app/scripts/main.py -launch_bot --name="YoungMouse" --debug_mode=True --advanced_logging=True
pause