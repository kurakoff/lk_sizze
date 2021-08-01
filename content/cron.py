import os
import sys
import datetime
sys.path.append('/var/www/html/lk_sizze/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'sizzy_lk.settings'

import django
django.setup()

from reversion.models import Version, Revision
from rest_framework.authtoken.models import Token


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
    os.system(f"mkdir /var/www/html/lk_sizze/backup/{today.month}-{today.year}")
    os.system(f'pg_dump -p 5432 lk_sizze > /var/www/html/lk_sizze/backup/{today.month}-{today.year}/db_{datetime.date.today()}.sql')
    return print("Создание backup оконченно")


if __name__ == "__main__":
    create_backup()