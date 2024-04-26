#!/bin/bash

source env/bin/activate
cd app/
python3 scripts/main.py -name YoungMouse

read -p "Press any key..."
