# Generated by Django 3.0.7 on 2021-05-12 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0034_auto_20210512_0553'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='theLastAppliedHeight',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='project',
            name='theLastAppliedWidth',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='screen',
            name='styles',
            field=models.TextField(default=''),
        ),
    ]
