#!/bin/bash
git pull
. venv/bin/activate
fuser -k 8000/tcp
echo yes | ./manage.py collectstatic
nohup ./manage.py runserver &






