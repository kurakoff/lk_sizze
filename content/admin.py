from django.contrib import admin
import nested_admin
from tinymce.widgets import TinyMCE

from .models import (
    Project,
    Screen,
    Prototype,
    Category,
    CategoryPrototype,
    Element,
)
from tinymce.models import HTMLField


class CategoryAdmin(admin.ModelAdmin):
    pass


class ElementInline(nested_admin.NestedTabularInline):
    model = Element
    extra = 0


class CategoryPrototypeInline(nested_admin.NestedStackedInline):
    model = CategoryPrototype
    inlines = [ElementInline]
    extra = 0


class PrototypeAdmin(nested_admin.NestedModelAdmin):
    inlines = [CategoryPrototypeInline]
    formfield_overrides = {
        HTMLField: {'widget': TinyMCE(attrs={'cols': 80, 'rows': 30})},
    }


admin.site.register(Prototype, PrototypeAdmin)
admin.site.register(Category, CategoryAdmin)
