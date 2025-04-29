poetry env activate
$env:PYTHONPATH = $PWD.Path

#python app/scripts/main.py -launch_bot --name=Test --debug_mode=True --advanced_logging=True
#poetry run python app/scripts/main.py -h
poetry run python app/main.py -launch_bot --name=Test
#poetry run python app/main.py -test
pause
