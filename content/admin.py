from django.contrib import admin
from .models import (
    Project,
    Screen,
    Prototype,
    GroupElements,
    Element,
)


class PrototypeAdmin(admin.ModelAdmin):
    pass


admin.site.register(Prototype, PrototypeAdmin)
