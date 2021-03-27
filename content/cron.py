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
                                                                       datetime.timedelta(days=14)))
    PastRevisions = Revision.objects.filter(date_created__lte=(datetime.datetime.now() -
                                                               datetime.timedelta(days=14)))
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
    os.system(f'sudo -i -u kabiljan; PGPASSWORD="kabiljan" pg_dump lk_sizze> /var/www/html/lk_sizze/backup/{today.month}-{today.year}/db_{datetime.date.today()}.bak')
    return print("Создание backup оконченно")


if __name__ == "__main__":
    create_backup()
