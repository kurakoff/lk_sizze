# Generated by Django 3.0.7 on 2021-03-26 13:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0022_modesstate_project'),
    ]

    operations = [
        migrations.CreateModel(
            name='Constant_colors',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dark_value', models.TextField()),
                ('light_value', models.TextField()),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='constant_colors', to='content.Project')),
            ],
        ),
        migrations.AddField(
            model_name='screen',
            name='constant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='screen_constant', to='content.Constant_colors'),
        ),
    ]
