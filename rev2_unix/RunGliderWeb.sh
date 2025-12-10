#!/bin/ksh

source .venv-sg/bin/activate

python make_db.py

python make_web.py

python send_website.py

deactivate
