# Generated by Django 3.0.7 on 2021-05-12 18:16

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0036_auto_20210512_1740'),
    ]

    operations = [
        migrations.AlterField(
            model_name='screen',
            name='styles',
            field=jsonfield.fields.JSONField(blank=True, null=True),
        ),
    ]
