# Generated by Django 3.0.7 on 2021-08-25 19:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0085_screen_screencategory_title'),
    ]

    operations = [
        migrations.RenameField(
            model_name='promocode',
            old_name='promo',
            new_name='promocode',
        ),
    ]