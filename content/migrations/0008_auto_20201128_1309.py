# Generated by Django 3.0.7 on 2020-11-28 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0007_screen_background_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='screen',
            name='background_color',
            field=models.TextField(default='#232323'),
        ),
    ]
