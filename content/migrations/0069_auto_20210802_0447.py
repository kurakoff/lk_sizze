# Generated by Django 3.0.7 on 2021-08-02 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0068_tasks_enterpriseuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tasks',
            name='status',
            field=models.CharField(choices=[('Done', 'Done'), ('In progress', 'In progress'), ('Not started', 'Not started')], default='NOT STARTED', max_length=100),
        ),
    ]