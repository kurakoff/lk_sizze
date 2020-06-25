#!/bin/bash

python3 manage.py migrate --settings=sizzy_lk.production_settings
python3 manage.py compress --settings=sizzy_lk.production_settings
echo yes | ./manage.py collectstatic
python3 manage.py runserver

#service nginx start
#uwsgi --ini uwsgi.ini






