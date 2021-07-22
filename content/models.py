import os.path

import jsonfield, reversion
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from . import models as this
CASCADE = models.CASCADE


def update_filename(instance, filename):
    path = 'firebase_credentials/'
    return f'{path}{instance.user}__{instance.project_id}.json'



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    google_album_id = models.CharField(max_length=100)


@reversion.register()
class UserElement(models.Model):
    title = models.CharField(max_length=36,  blank=False)
    layout = models.TextField(default='')
    project = models.ForeignKey('Project', on_delete=models.CASCADE, default=None)
    type = models.TextField(null=True, default=None)


@reversion.register(follow=['screen_set', 'userelement_set', 'modes_state', 'constant_colors'])
class Project(models.Model):
    name = models.CharField(max_length=255, verbose_name='name', blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prototype = models.ForeignKey('Prototype', on_delete=models.CASCADE)
    colors = jsonfield.JSONField()
    count = models.IntegerField(verbose_name='version period', default=0)
    theLastAppliedWidth = models.IntegerField(default=0)
    theLastAppliedHeight = models.IntegerField(default=0)
    previewScreenId = models.ForeignKey("Screen", related_name='project_preview', on_delete=models.SET_NULL, default=None, null=True, blank=True)

    class Meta:
        verbose_name = 'project'
        verbose_name_plural = 'projects'

    def __str__(self):
        return str(self.name)


class BaseWidthPrototype(models.Model):
    title = models.CharField(max_length=255)
    width = models.IntegerField()
    light_image = models.FileField(upload_to='images_prototype_width/', verbose_name='light image')
    dark_image = models.FileField(upload_to='images_prototype_width/', verbose_name='dark image')

    def __str__(self):
        return str(self.title)


class Prototype(models.Model):
    device_name = models.CharField(max_length=64, verbose_name='name')
    width = models.IntegerField(verbose_name='width', default=0)
    height = models.IntegerField(verbose_name='height', default=0)
    image = models.FileField(upload_to='images_prototypes/', verbose_name='image')
    image_hover = models.FileField(upload_to='images_prototypes/hover/', verbose_name='hover', default='')
    base_width = models.ManyToManyField(BaseWidthPrototype, null=True, verbose_name='base width')

    class Meta:
        verbose_name = 'prototype'
        verbose_name_plural = 'prototypes'

    def __str__(self):
        return str(self.device_name)
    #
    # @property
    # def created_categories(self):
    #     return self.categoryprototype_set.values_list('pk', flat=True)


@reversion.register()
class Constant_colors(models.Model):
    title = models.CharField(max_length=255, default='')
    dark_value = models.TextField()
    light_value = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='constant_colors', null=True, blank=True)
    to_prototype = models.ForeignKey(Prototype, on_delete=models.CASCADE, related_name='constant_prototype', null=True,
                                     blank=True)

    class Meta:
        verbose_name = 'color'
        verbose_name_plural = 'colors'

    def __str__(self):
        return str(self.title)

@reversion.register()
class Screen(models.Model):
    title = models.CharField(max_length=32, verbose_name='title', default='')
    layout = models.TextField(verbose_name='layout', default='')
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    last_change = models.DateTimeField(verbose_name='last change', default=now)
    width = models.IntegerField(verbose_name='width', default=0)
    height = models.IntegerField(verbose_name='height', default=0)
    background_color = models.TextField(default='#FFFFFF')
    position = models.IntegerField(verbose_name='position', default=0)
    constant_color = models.ForeignKey(Constant_colors, on_delete=models.CASCADE, related_name='constant_screen',
                                       null=True, blank=True)
    styles = jsonfield.JSONField(null=True, blank=True)
    base = models.CharField(max_length=50, default=0)

    class Meta:
        verbose_name = 'screen'
        verbose_name_plural = 'screens'

    def __str__(self):
        return str(self.pk)


class Category(models.Model):
    title = models.CharField(max_length=64, verbose_name='title')
    slug = models.CharField(max_length=64, verbose_name='slug')
    two_in_row = models.BooleanField(verbose_name='2 elements', default=False)
    prototype = models.ManyToManyField(Prototype, null=True, verbose_name='prototypes')

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.title


class Element(models.Model):
    title = models.CharField(max_length=64, verbose_name='title')
    category_prototype = models.ForeignKey('Category', on_delete=CASCADE, default=1, null=True)
    light_image = models.FileField(upload_to='images_elements/', verbose_name='light_cover')
    dark_image = models.FileField(upload_to='images_elements/', verbose_name='dark_cover')
    light_layout = models.TextField(verbose_name='light_layout')
    dark_layout = models.TextField(verbose_name='dark_layout')
    active = models.BooleanField(verbose_name='on', default=True)

    class Meta:
        verbose_name = 'element'
        verbose_name_plural = 'elements'

    def __str__(self):
        return self.title


class Settings(models.Model):
    value = models.PositiveIntegerField(verbose_name='value', blank=False)
    slug = models.CharField(max_length=64, verbose_name='slug')

    class Meta:
        verbose_name = 'setting'
        verbose_name_plural = 'settings'

    def __str__(self):
        return self.slug


class SocialUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='social_user')
    provider = models.CharField(verbose_name='provider', max_length=50)

    class Meta:
        verbose_name = 'social user'
        verbose_name_plural = 'social users'

    def __str__(self):
        return self.provider


class SharedProject(models.Model):
    from_user = models.ForeignKey(User, to_field='email', on_delete=models.CASCADE, related_name='from_user')
    to_user = models.ForeignKey(User, to_field='email', on_delete=models.CASCADE, related_name='to_user', null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='share_project')
    permission = jsonfield.JSONField()
    all_users = models.BooleanField()

    def __str__(self):
        return str(self.project)

    class Meta:
        verbose_name = 'shared project'
        verbose_name_plural = 'shared projects'


class PasswordReset(models.Model):
    to_user = models.ForeignKey(User, to_field='email', on_delete=models.CASCADE, related_name="reset_to_user")
    pin = models.CharField(max_length=6, unique=True)
    activate = models.BooleanField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.pin


@reversion.register()
class ModesState(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='modes_state')
    elements = models.TextField()


class FigmaUser(models.Model):
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    figma_user = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class ClientStrip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.CharField(max_length=255)
    seanse = models.TextField()
    livemode = models.BooleanField()
    use_trial = models.BooleanField()


class Price(models.Model):
    price = models.CharField(max_length=500)
    product = models.CharField(max_length=500)
    status = models.CharField(max_length=255)
    live_mode = models.BooleanField()
    cost = models.IntegerField()
    interval = models.CharField(max_length=255)
    name = models.TextField()


class Subscription(models.Model):
    subscription = models.CharField(max_length=500)
    plan = models.ForeignKey(Price, on_delete=models.CASCADE)
    end_period = models.CharField(max_length=100)
    start_period = models.CharField(max_length=100)
    customer = models.ForeignKey(ClientStrip, on_delete=models.CASCADE)
    latest_invoice = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    subscription_end = models.CharField(max_length=255, null=True)
    livemode = models.BooleanField()


class UserPermission(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    start = models.BooleanField(default=True)
    professional = models.BooleanField(default=False)
    team = models.BooleanField(default=False)
    last_update = models.DateTimeField(null=True, default=None)
    downloadCount = models.IntegerField(default=0)


class UserAbout(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profession = models.CharField(null=True, blank=True, default=None, max_length=30)
    framework = models.CharField(null=True, blank=True, default=None, max_length=30)
    news = models.CharField(null=True, blank=True, default=None, max_length=255)
    theme = models.CharField(null=True, blank=True, default=None, max_length=30)

    class Meta:
        verbose_name = 'questionnaire'
        verbose_name_plural = 'questionnaires'

    def __str__(self):
        return str(self.user)


class Request(models.Model):
    request_type = models.CharField(max_length=100)
    header = models.TextField(blank=True, null=True)
    url = models.TextField()
    title = models.CharField(max_length=255, blank=True, null=True)
    data = models.TextField(blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    backendType = models.TextField(blank=True, null=True)


class FirebaseSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    credentials_file = models.FileField(upload_to=update_filename, unique=True, blank=True)
    credentials = jsonfield.JSONField(blank=True)

    def __str__(self):
        return str(self.user.email)


class FirebaseRequest(models.Model):
    request = models.ForeignKey(FirebaseSettings, on_delete=models.CASCADE)
    collection = models.CharField(max_length=255)
    fields = jsonfield.JSONField(null=True, blank=True)
