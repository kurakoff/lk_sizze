# Generated by Django 3.0.7 on 2021-08-21 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0082_auto_20210821_1655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='screen_screencategory',
            name='image',
            field=models.FileField(null=True, upload_to='Screen_category/'),
        ),
        migrations.AlterField(
            model_name='screen_screencategory',
            name='position',
            field=models.SmallIntegerField(default=0),
        ),
    ]
