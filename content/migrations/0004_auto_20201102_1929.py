# Generated by Django 3.0.7 on 2020-11-02 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0003_auto_20201102_1928'),
    ]

    operations = [
        migrations.AddField(
            model_name='element',
            name='dark_image',
            field=models.FileField(default='', upload_to='images_elements/', verbose_name='dark_cover'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='element',
            name='dark_layout',
            field=models.TextField(default='', verbose_name='dark_макет'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='element',
            name='light_image',
            field=models.FileField(upload_to='images_elements/', verbose_name='light_cover'),
        ),
        migrations.AlterField(
            model_name='element',
            name='light_layout',
            field=models.TextField(verbose_name='light_макет'),
        ),
    ]
