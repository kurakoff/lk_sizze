# Generated by Django 3.0.7 on 2021-05-12 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0033_auto_20210512_0509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='subscription_end',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
