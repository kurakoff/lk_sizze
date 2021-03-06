import jsonfield
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
import reversion

CASCADE = models.CASCADE


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    google_album_id = models.CharField(max_length=100)


class UserElement(models.Model):
    title = models.CharField(max_length=36,  blank=False)
    layout = models.TextField(default='')
    project = models.ForeignKey('Project', on_delete=models.CASCADE, default=None)


class Project(models.Model):
    name = models.CharField(max_length=16, verbose_name='название', blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prototype = models.ForeignKey('Prototype', on_delete=models.CASCADE)
    colors = jsonfield.JSONField()

    class Meta:
        verbose_name = 'проект'
        verbose_name_plural = 'проекты'

    def __str__(self):
        return str(self.name)


@reversion.register()
class Screen(models.Model):
    title = models.CharField(max_length=32, verbose_name='название', default='')
    layout = models.TextField(verbose_name='макет', default='')
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    last_change = models.DateTimeField(verbose_name='последние изменение', default=now)
    width = models.IntegerField(verbose_name='ширина', default=0)
    height = models.IntegerField(verbose_name='высота', default=0)
    background_color = models.TextField(default='#FFFFFF')
    position = models.IntegerField(verbose_name='позиция', default=0)

    class Meta:
        verbose_name = 'экран'
        verbose_name_plural = 'экраны'

    def __str__(self):
        return str(self.pk)


class Prototype(models.Model):
    device_name = models.CharField(max_length=64, verbose_name='название')
    width = models.IntegerField(verbose_name='ширина', default=0)
    height = models.IntegerField(verbose_name='высота', default=0)
    image = models.FileField(upload_to='images_prototypes/', verbose_name='изображение')
    image_hover = models.FileField(upload_to='images_prototypes/hover/', verbose_name='hover', default='')

    class Meta:
        verbose_name = 'прототип'
        verbose_name_plural = 'прототипы'

    def __str__(self):
        return str(self.device_name)
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


class SocialUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='social_user')
    provider = models.CharField(verbose_name='Провайдер', max_length=50)

    class Meta:
        verbose_name = 'Социальный пользователь'
        verbose_name_plural = 'Социальные пользователи'

    def __str__(self):
        return self.provider


class SharedProject(models.Model):
    from_user = models.ForeignKey(User, to_field='email', on_delete=models.CASCADE, related_name='from_user')
    to_user = models.ForeignKey(User, to_field='email', on_delete=models.CASCADE, related_name='to_user', null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='share_project')
    permission = jsonfield.JSONField()
    all_users = models.BooleanField()

    def __str__(self):
        return self.project


class PasswordReset(models.Model):
    to_user = models.ForeignKey(User, to_field='email', on_delete=models.CASCADE, related_name="reset_to_user")
    pin = models.CharField(max_length=6, unique=True)
    activate = models.BooleanField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.to_user
