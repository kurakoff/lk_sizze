from django.contrib.auth.models import User
from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=16, verbose_name='название', blank=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    prototype_id = models.ForeignKey('Prototype', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'проект'
        verbose_name_plural = 'проекты'

    def __str__(self):
        return self.name


class Screen(models.Model):
    layout_screen = models.TextField(verbose_name='макет')
    project_id = models.ForeignKey('Project', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'экран'
        verbose_name_plural = 'экраны'

    def __str__(self):
        return self.pk


class Prototype(models.Model):
    device_name = models.CharField(max_length=64, verbose_name='название')
    image = models.FileField(upload_to='images_prototypes/', verbose_name='изображение')

    class Meta:
        verbose_name = 'прототип'
        verbose_name_plural = 'прототипы'

    def __str__(self):
        return self.device_name


# TODO: Продумать структуру привязки групп элементов


class GroupElements(models.Model):
    title = models.CharField(max_length=64, verbose_name='название')
    prototype_id = models.ForeignKey('Prototype', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'группа'
        verbose_name_plural = 'группы'

    def __str__(self):
        return self.title


class Element(models.Model):
    title = models.CharField(max_length=64, verbose_name='название')
    group_id = models.ForeignKey('GroupElements', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images_elements/', verbose_name='изображение')
    layout_element = models.TextField(verbose_name='макет')

    class Meta:
        verbose_name = 'графический элемент'
        verbose_name_plural = 'графические элементы'

    def __str__(self):
        return self.title
