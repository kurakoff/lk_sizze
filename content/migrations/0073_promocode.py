# Generated by Django 3.0.7 on 2021-08-05 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0072_auto_20210804_1515'),
    ]

    operations = [
        migrations.CreateModel(
            name='Promocode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('promo', models.CharField(max_length=5, unique=True)),
                ('activate', models.CharField(default=None, max_length=5, null=True)),
                ('activated', models.IntegerField(default=0)),
            ],
        ),
    ]