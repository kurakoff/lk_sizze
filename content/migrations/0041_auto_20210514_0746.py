# Generated by Django 3.0.7 on 2021-05-14 07:46

from django.db import migrations
from content.models import UserPermission
from django.contrib.auth.models import User


def add_perms(apps, schema_editor):
    UserPermission.objects.bulk_create([UserPermission(user_id=user_id) for user_id in User.objects.values_list("id", flat=True)], ignore_conflicts=True)


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0040_auto_20210514_0745'),
    ]

    operations = [
        migrations.RunPython(add_perms)
    ]
