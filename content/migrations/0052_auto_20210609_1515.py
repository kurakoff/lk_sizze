# Generated by Django 3.0.7 on 2021-06-09 15:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0051_auto_20210609_1504'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='previewScreenId',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='project_preview', to='content.Screen'),
        ),
    ]