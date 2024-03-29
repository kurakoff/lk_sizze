# Generated by Django 3.0.7 on 2021-02-22 14:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('content', '0012_auto_20210216_0829'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sharedproject',
            name='from_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_user', to=settings.AUTH_USER_MODEL, to_field='email'),
        ),
        migrations.AlterField(
            model_name='sharedproject',
            name='to_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='to_user', to=settings.AUTH_USER_MODEL, to_field='email'),
        ),
    ]
