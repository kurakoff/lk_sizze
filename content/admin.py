from django.contrib import admin
import nested_admin
from .models import (
    Project,
    Screen,
    Prototype,
    Category,
    CategoryPrototype,
    Element,
)


class CategoryAdmin(admin.ModelAdmin):
    pass


class ElementInline(nested_admin.NestedStackedInline):
    model = Element
    extra = 0


class CategoryPrototypeInline(nested_admin.NestedStackedInline):
    model = CategoryPrototype
    inlines = [ElementInline]
    extra = 0


class PrototypeAdmin(nested_admin.NestedModelAdmin):
    inlines = [CategoryPrototypeInline]


admin.site.register(Prototype, PrototypeAdmin)
admin.site.register(Category, CategoryAdmin)
