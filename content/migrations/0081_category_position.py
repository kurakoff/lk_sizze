# Generated by Django 3.0.7 on 2021-08-19 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0080_screencategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='position',
            field=models.SmallIntegerField(default=0),
        ),
    ]
