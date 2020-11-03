from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from tinymce.models import HTMLField
from django.utils.timezone import now
from tinymce.widgets import TinyMCE

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
    title = models.CharField(max_length=32, verbose_name='название', default='')
    layout = models.TextField(verbose_name='макет', default='')
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    last_change = models.DateTimeField(verbose_name='последние изменение', default=now)

    class Meta:
        verbose_name = 'экран'
        verbose_name_plural = 'экраны'

    def __str__(self):
        return self.pk

    def base_layout(self):
        return self.project.prototype.base_layout


class Prototype(models.Model):
    device_name = models.CharField(max_length=64, verbose_name='название')
    base_layout = HTMLField(verbose_name='начальный макет', default='')
    image = models.FileField(upload_to='images_prototypes/', verbose_name='изображение')
    image_hover = models.FileField(upload_to='images_prototypes/hover/', verbose_name='hover', default='')

    class Meta:
        verbose_name = 'прототип'
        verbose_name_plural = 'прототипы'

    def __str__(self):
        return self.device_name
    #
    # @property
    # def created_categories(self):
    #     return self.categoryprototype_set.values_list('pk', flat=True)


class Category(models.Model):
    title = models.CharField(max_length=64, verbose_name='название')
    slug = models.CharField(max_length=64, verbose_name='slug')
    two_in_row = models.BooleanField(verbose_name='По 2 элемента', default=False)

    class Meta:
        verbose_name = 'картегория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.title

    def get_elements_on_prototype(self, prototype_id):
        return Element.objects.filter(category_prototype__category=self.id,
                                      category_prototype__prototype=prototype_id).all()


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
    light_image = models.FileField(upload_to='images_elements/', verbose_name='light_cover')
    dark_image = models.FileField(upload_to='images_elements/', verbose_name='dark_cover')
    # TODO: сделать редактор кода
    light_layout = models.TextField(verbose_name='light_макет')
    dark_layout = models.TextField(verbose_name='dark_макет')
    active = models.BooleanField(verbose_name='on', default=True)

    class Meta:
        verbose_name = 'графический элемент'
        verbose_name_plural = 'графические элементы'

    def __str__(self):
        return self.title


class Settings(models.Model):
    value = models.PositiveIntegerField(verbose_name='Значение', blank=False)
    slug = models.CharField(max_length=64, verbose_name='slug')

    class Meta:
        verbose_name = 'настройка'
        verbose_name_plural = 'настройки'

    def __str__(self):
        return self.slug
