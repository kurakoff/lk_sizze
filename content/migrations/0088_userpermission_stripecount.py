# Generated by Django 3.0.7 on 2021-11-28 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0087_auto_20210827_1529'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpermission',
            name='stripeCount',
            field=models.SmallIntegerField(default=0),
        ),
    ]