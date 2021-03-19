#!/bin/bash
apt-get update -y
sudo apt install python3-pip
sudo apt-get install python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
sudo apt install gunicorn3
gunicorn3 --workers=4 --bind=0.0.0.0:5000 app:app
