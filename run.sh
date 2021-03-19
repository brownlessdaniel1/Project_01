#!/bin/bash
sudo apt-get update
sudo apt install python3-pip
python3 -m venv .venv
source .venv/bin/activate
python3 
pip3 install -r requirements.txt
gunicorn --workers=4 --bind=0.0.0.0:5000 app:app
