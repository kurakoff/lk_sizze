# Generated by Django 3.0.7 on 2021-08-25 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0084_auto_20210823_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='screen_screencategory',
            name='title',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
