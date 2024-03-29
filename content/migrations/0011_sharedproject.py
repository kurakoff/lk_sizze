# Generated by Django 3.0.7 on 2021-01-13 17:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('content', '0010_auto_20210112_1804'),
    ]

    operations = [
        migrations.CreateModel(
            name='SharedProject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission', jsonfield.fields.JSONField(default=dict)),
                ('all_users', models.BooleanField()),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='my_project', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shared_projects', to='content.Project')),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shared_project', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
