# Generated by Django 3.0.7 on 2021-05-14 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0039_userpermission'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpermission',
            name='last_update',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='userpermission',
            name='professional',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='userpermission',
            name='team',
            field=models.BooleanField(default=False),
        ),
    ]
