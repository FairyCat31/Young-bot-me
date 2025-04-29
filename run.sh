#!/bin/bash

poetry env activate
export PYTHONPATH=$(pwd)
poetry run python app/scripts/main.py -launch_bot --name=Test

read -p "Press any key..."
