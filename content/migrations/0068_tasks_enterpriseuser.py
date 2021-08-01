# Generated by Django 3.0.7 on 2021-08-01 10:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0067_enterpriseuser_tasks'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasks',
            name='enterpriseUser',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='content.EnterpriseUser'),
            preserve_default=False,
        ),
    ]
