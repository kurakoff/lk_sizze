# Generated by Django 3.0.7 on 2021-04-02 13:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0025_auto_20210329_0956'),
    ]

    operations = [
        migrations.RenameField(
            model_name='screen',
            old_name='constant',
            new_name='constant_color',
        ),
    ]