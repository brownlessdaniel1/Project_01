#!/bin/bash
sudo apt-get update
cd todolists/
python3 -m venv .venv
. ./.venv/bin/activate
pip3 install -r requirements.txt
export SQL_URI="sqlite:///test-db"
gunicorn --workers=4 --bind=0.0.0.0:5000 app:app