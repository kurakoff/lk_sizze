# Generated by Django 3.0.7 on 2021-03-29 09:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0024_auto_20210327_1608'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='screen',
            name='constant',
        ),
        migrations.AddField(
            model_name='screen',
            name='constant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='constant_screen', to='content.Constant_colors'),
        ),
    ]
