import os
import sys
import datetime
sys.path.append('/var/www/html/lk_sizze/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'sizzy_lk.settings'

import django
django.setup()

from reversion.models import Version, Revision
from rest_framework.authtoken.models import Token
from content import models


def delete_past_project():
    print("Начато удаленние старых версий проектов")
    PastProjects = Version.objects.filter(revision__date_created__lte=(datetime.datetime.now() -
                                                                       datetime.timedelta(days=14)),
                                          revision__user__user_permission__start=True)
    PastRevisions = Revision.objects.filter(date_created__lte=(datetime.datetime.now() -
                                                               datetime.timedelta(days=14)),
                                            user__user_permission__start=True)
    PastProjects.delete()
    PastRevisions.delete()
    return print("Удаленние старых проектов завершенно")


def delete_past_tokens():
    print("Начато удаленние старых токенов")
    pastToken = Token.objects.filter(created__lte=(datetime.datetime.now() -
                                                   datetime.timedelta(days=30)))
    pastToken.delete()
    return print("Удаленние старых токенов завершенно")


def create_backup():
    today = datetime.datetime.today()
    print("Начато создание backup базы данных ", today)
    directory = f"/var/www/html/lk_sizze/backup/{today.month}-{today.year}"
    if os.path.exists(directory) is False:
        os.system(f"mkdir {directory}")
    os.system(f"echo K5xv2Ak763 | sudo -S chmod 777 /var/www/html/lk_sizze/backup/{today.month}-{today.year}")
    os.system(f'pg_dump -F c -p 5432 lk_sizze > /var/www/html/lk_sizze/backup/{today.month}-{today.year}/db_{datetime.date.today()}.sql')
    return print("Создание backup оконченно")


def stop_free_moth():
    print("Начата отмена бесплатных подписок")
    promos = models.Promocode.objects.filter(end_date__lt=datetime.date.today())
    for promo in promos:
        perm = promo.user.userpermission
        perm.permission = "START"
        perm.save()
    return print("Бесплатные подписки отменены")


def update_test_bd():
    print("Начато обновление бд тестового сервера")
    today = datetime.datetime.today()
    os.system(f"cd /var/www/html/lk_sizze/backup")
    os.system(f"sshpass -p 'K5xv2Ak763' scp sergey@89.223.122.154:/var/www/html/lk_sizze/backup/{today.month}-{today.year}"
              f"/db_{datetime.date.today() - datetime.timedelta(days=1)}.sql /var/www/html/lk_sizze/backup")
    os.system(f"PGPASSWORD=K5xv2Ak763 dropdb --username postgres 'lk_sizze'")
    os.system(f"echo K5xv2Ak763 | sudo -S -u postgres PGPASSWORD=K5xv2Ak763 psql -c 'create database lk_sizze;'")
    os.system(f"echo K5xv2Ak763 | sudo -S -u postgres PGPASSWORD=K5xv2Ak763 psql -c 'grant all privileges on database lk_sizze to sergey;'")
    os.system(f"PGPASSWORD=K5xv2Ak763 pg_restore -d lk_sizze -U sergey -C db_{datetime.date.today() - datetime.timedelta(days=1)}.sql")
    print("Закончато обновление бд тестового сервера")


if __name__ == "__main__":
    update_test_bd()