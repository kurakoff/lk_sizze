# Generated by Django 3.0.7 on 2021-03-23 06:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0021_modesstate'),
    ]

    operations = [
        migrations.AddField(
            model_name='modesstate',
            name='project',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='modes_state', to='content.Project'),
            preserve_default=False,
        ),
    ]
