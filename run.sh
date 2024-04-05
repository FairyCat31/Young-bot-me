#!/bin/bash

source env/bin/activate
cd app/
python3.11 scripts/main.py

read -p "Press any key..."
