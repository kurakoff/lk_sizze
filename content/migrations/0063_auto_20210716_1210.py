# Generated by Django 3.0.7 on 2021-07-16 12:10

import content.models
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0062_firebasesettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='firebasesettings',
            name='credentials',
            field=jsonfield.fields.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='firebasesettings',
            name='credentials_file',
            field=models.FileField(blank=True, unique=True, upload_to=content.models.update_filename),
        ),
        migrations.CreateModel(
            name='FirebaseRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collection', models.CharField(max_length=255)),
                ('fields', jsonfield.fields.JSONField(blank=True, null=True)),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='content.FirebaseSettings')),
            ],
        ),
    ]