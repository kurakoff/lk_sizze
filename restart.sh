#!/bin/bash
cd /var/www/html/lk_sizze/ || exit
fuser -k 8000/tcp
git pull
. venv/bin/activate
echo yes | ./manage.py collectstatic
nohup python manage.py runserver &
