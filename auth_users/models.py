from django.contrib.auth.models import User
from django.db import models

User._meta.get_field('email')._unique = True
User._meta.get_field('username')._unique = False
