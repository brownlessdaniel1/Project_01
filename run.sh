#!/bin/bash
sudo apt-get update
sudo apt install python3-pip
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
sudo apt install gunicorn
gunicorn --workers=2 --bind=0.0.0.0:5000 app:app
