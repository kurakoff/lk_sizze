# Generated by Django 3.0.7 on 2020-06-24 22:45

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('content', '0003_auto_20200624_2221'),
    ]

    operations = [
        migrations.RenameField(
            model_name='element',
            old_name='group_id',
            new_name='group',
        ),
        migrations.RenameField(
            model_name='groupelements',
            old_name='prototype_id',
            new_name='prototype',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='prototype_id',
            new_name='prototype',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='user_id',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='screen',
            old_name='project_id',
            new_name='project',
        ),
    ]
