#!/bin/bash
sudo apt-get update -y
sudo apt-get install -y python3-venv python3-pip
python3 -m venv .venv
. .venv/bin/activate
pip3 install -r requirements.txt
gunicorn --workers=4 --bind=0.0.0.0:5000 app:app
