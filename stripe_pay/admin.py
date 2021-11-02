from django.contrib import admin
from content.models import ClientStrip


class StripeSettings(admin.ModelAdmin):
    list_display = ['client']


admin.site.register(ClientStrip, StripeSettings)