from django.contrib import admin
import nested_admin
from tinymce.widgets import TinyMCE
from reversion.admin import VersionAdmin

from .models import (
    SharedProject,
    Project,
    Screen,
    Prototype,
    Category,
    CategoryPrototype,
    Element,
    Settings,
)
from tinymce.models import HTMLField


class CategoryAdmin(admin.ModelAdmin):
    pass


class SettingsAdmin(admin.ModelAdmin):
    list_display = ('slug', 'value')
    # readonly_fields = ('slug',)

    def has_delete_permission(self, request, obj=None):
        return False


class ElementInline(nested_admin.NestedTabularInline):
    model = Element
    extra = 0


class CategoryPrototypeInline(nested_admin.NestedStackedInline):
    model = CategoryPrototype
    inlines = [ElementInline]
    extra = 0

    # def get_queryset(self, request):
    #     qs = super(CategoryPrototypeInline, self).get_queryset(request)
    #     created_categories = self.parent_obj.created_categories
    #     print(list(created_categories))
    #     qs.filter(pk__notin=list(created_categories))
    #     print(qs)
    #     return qs
    #
    # def get_formset(self, request, obj=None, **kwargs):
    #     self.parent_obj = obj
    #     return super(CategoryPrototypeInline, self).get_formset(request, obj, **kwargs)


class PrototypeAdmin(nested_admin.NestedModelAdmin):
    inlines = [CategoryPrototypeInline]
    formfield_overrides = {
        HTMLField: {'widget': TinyMCE(attrs={'cols': 80, 'rows': 30})},
    }


@admin.register(Screen)
class ClientModelAdmin(VersionAdmin):
    pass

admin.site.register(Prototype, PrototypeAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Settings, SettingsAdmin)
admin.site.register(Project)
admin.site.register(SharedProject)
admin.site.register(Element)
