#!/bin/bash


python3.11 -m venv env
source env/bin/activate
pip3.11 install -r app/data/sys/req.txt

read -p "Press any key..."
