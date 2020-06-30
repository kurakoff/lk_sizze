from django.contrib.auth.models import User
from django.db import models

CASCADE = models.CASCADE


class Project(models.Model):
    name = models.CharField(max_length=16, verbose_name='название', blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prototype = models.ForeignKey('Prototype', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'проект'
        verbose_name_plural = 'проекты'

    def __str__(self):
        return self.name


class Screen(models.Model):
    layout_screen = models.TextField(verbose_name='макет')
    project = models.ForeignKey('Project', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'экран'
        verbose_name_plural = 'экраны'

    def __str__(self):
        return self.pk


class Prototype(models.Model):
    device_name = models.CharField(max_length=64, verbose_name='название')
    image = models.FileField(upload_to='images_prototypes/', verbose_name='изображение')
    image_hover = models.FileField(upload_to='images_prototypes/hover/', verbose_name='hover', default='')

    class Meta:
        verbose_name = 'прототип'
        verbose_name_plural = 'прототипы'

    def __str__(self):
        return self.device_name


class Category(models.Model):
    title = models.CharField(max_length=64, verbose_name='название')
    slug = models.CharField(max_length=64, verbose_name='slug')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'картегория'
        verbose_name_plural = 'категории'


class CategoryPrototype(models.Model):
    category = models.ForeignKey('Category', on_delete=CASCADE, verbose_name='категория')
    prototype = models.ForeignKey('Prototype', on_delete=CASCADE)

    class Meta:
        verbose_name = 'картегория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.category.title


class Element(models.Model):
    title = models.CharField(max_length=64, verbose_name='название')
    category_prototype = models.ForeignKey('CategoryPrototype', on_delete=CASCADE, default=1)
    image = models.ImageField(upload_to='images_elements/', verbose_name='изображение')
    # TODO: сделать редактор кода
    layout_element = models.TextField(verbose_name='макет')

    class Meta:
        verbose_name = 'графический элемент'
        verbose_name_plural = 'графические элементы'

    def __str__(self):
        return self.title
