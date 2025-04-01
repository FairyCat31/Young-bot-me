#!/bin/bash

source env/bin/activate
export PYTHONPATH=$(pwd)
echo $(pwd)
python3 app/scripts/main.py -launch_bot --name=Test --debug_mode=True --advanced_logging=True

read -p "Press any key..."
