import os.path

import jsonfield, reversion
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
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

    class Meta:
        verbose_name = 'user element'
        verbose_name_plural = 'user elements'


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

    class Meta:
        verbose_name = 'base width of prototypes'
        verbose_name_plural = 'base width of the prototype'

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
    position = models.SmallIntegerField(default=0)

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

    class Meta:
        verbose_name = 'password reset'
        verbose_name_plural = 'password resets'

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

    class Meta:
        verbose_name = 'figma user'
        verbose_name_plural = 'figma users'


class ClientStrip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.CharField(max_length=255)
    seanse = models.TextField()
    livemode = models.BooleanField()
    use_trial = models.BooleanField()

    class Meta:
        verbose_name = 'client stripe'
        verbose_name_plural = 'stripe clients'


class Price(models.Model):
    price = models.CharField(max_length=500)
    product = models.CharField(max_length=500)
    status = models.CharField(max_length=255)
    live_mode = models.BooleanField()
    cost = models.IntegerField()
    interval = models.CharField(max_length=255)
    name = models.TextField()

    class Meta:
        verbose_name = 'price'
        verbose_name_plural = 'prices'


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

    class Meta:
        verbose_name = 'subscription'
        verbose_name_plural = 'subscriptions'


class UserPermission(models.Model):
    CHOICES = (
        ('START', 'start'),
        ('PROFESSIONAL', 'professional'),
        ('TEAM', 'team'),
        ('ENTERPRISE', 'enterprise')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    permission = models.CharField(max_length=25, choices=CHOICES, default='START')
    last_update = models.DateTimeField(null=True, default=None)
    downloadCount = models.IntegerField(default=0)
    isVideoExamplesDisabled = models.BooleanField(default=False)
    copyCount = models.IntegerField(default=0)
    stripeCount = models.SmallIntegerField(default=0)

    class Meta:
        verbose_name = 'user permission'
        verbose_name_plural = 'user permissions'


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

    class Meta:
        verbose_name = 'request'
        verbose_name_plural = 'requests'


class FirebaseSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    credentials = jsonfield.JSONField(blank=True)

    class Meta:
        verbose_name = 'firebase settings'
        verbose_name_plural = 'firebase settings'

    def __str__(self):
        return str(self.user.email)


class FirebaseRequest(models.Model):
    request = models.ForeignKey(FirebaseSettings, on_delete=models.CASCADE)
    collection = models.CharField(max_length=255)
    fields = jsonfield.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = 'firebase request'
        verbose_name_plural = 'firebase requests'


class EnterpriseUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    telegram = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'enterprise user'
        verbose_name_plural = 'enterprise users'

    def __str__(self):
        return str(self.user.email)


class Tasks(models.Model):
    CHOICES = (
        ('Done', 'Done'),
        ('In progress', 'In progress'),
        ('Not started', 'Not started')
    )
    enterpriseUser = models.ForeignKey(EnterpriseUser, on_delete=models.CASCADE)
    stage = models.CharField(max_length=255, null=True)
    update = models.DateField(default=now)
    status = models.CharField(max_length=100, choices=CHOICES, default="NOT STARTED")
    description = models.TextField(null=True)

    class Meta:
        verbose_name = 'task'
        verbose_name_plural = 'tasks'


class Tutorials(models.Model):
    name = models.CharField(max_length=255)
    source = models.CharField(max_length=255, null=True)

    class Meta:
        verbose_name = 'tutorial'
        verbose_name_plural = 'tutorials'


class Promocode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='promocode')
    promocode = models.CharField(unique=True, max_length=5)
    activate = models.CharField(max_length=5, null=True, default=None)
    activated = models.IntegerField(default=0)
    discount = models.BooleanField(default=False)
    free_month = models.BooleanField(default=False)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    class Meta:
        verbose_name = 'promo code'
        verbose_name_plural = 'promo codes'


class PluginAuth(models.Model):
    key = models.CharField(max_length=255, unique=True)
    write = models.CharField(max_length=255, unique=True)


class ScreenCategory(models.Model):
    title = models.CharField(max_length=255)
    screen = models.ManyToManyField(Screen, through="Screen_ScreenCategory")
    active = models.BooleanField(default=False)
    position = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'screen category'
        verbose_name_plural = 'screen categories'


class Screen_ScreenCategory(models.Model):
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE)
    screencategory = models.ForeignKey(ScreenCategory, on_delete=models.CASCADE)
    image = models.FileField(upload_to='screen_category/', null=True)
    position = models.SmallIntegerField(default=0)
    title = models.CharField(max_length=255, null=True)
