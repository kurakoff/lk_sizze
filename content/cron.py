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


if __name__ == "__main__":
    delete_past_project()
    delete_past_tokens()
