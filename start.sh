#!/bin/bash

python manage.py migrate --settings=sizzy_lk.production_settings
python manage.py compress --settings=sizzy_lk.production_settings
echo yes | ./manage.py collectstatic
python manage.py runserver

#service nginx start
#uwsgi --ini uwsgi.ini






