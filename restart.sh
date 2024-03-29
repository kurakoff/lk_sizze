#!/bin/bash
cd /var/www/html/lk_sizze/ || exit
fuser -k 8000/tcp
git pull
. venv/bin/activate
python3 manage.py migrate --settings=sizzy_lk.production_settings
python3 manage.py crontab remove
python3 manage.py crontab add
echo yes | ./manage.py collectstatic
nohup python manage.py runserver &
