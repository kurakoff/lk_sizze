# Generated by Django 3.0.7 on 2021-03-16 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0017_project_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(max_length=255, verbose_name='название'),
        ),
    ]
