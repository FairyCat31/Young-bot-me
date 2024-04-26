#!/bin/bash


python3 -m venv env
source env/bin/activate
pip3 install -r app/data/sys/req.txt

read -p "Press any key..."
