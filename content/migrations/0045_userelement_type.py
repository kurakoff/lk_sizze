# Generated by Django 3.0.7 on 2021-05-22 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0044_remove_clientstrip_payment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='userelement',
            name='type',
            field=models.TextField(default=None, null=True),
        ),
    ]
