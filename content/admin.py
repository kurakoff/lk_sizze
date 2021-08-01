from django.contrib import admin
import nested_admin
from tinymce.widgets import TinyMCE
from reversion.models import Revision, Version
from simple_sso.sso_server.models import Token as ssoToken
from .models import (
    SharedProject,
    Project,
    Screen,
    Prototype,
    Category,
    Element,
    Settings,
    BaseWidthPrototype,
    Constant_colors,
    ModesState,
    FigmaUser,
    PasswordReset,
    ClientStrip,
    Price,
    Subscription,
    UserPermission,
    UserAbout,
    FirebaseSettings,
    FirebaseRequest
)
from tinymce.models import HTMLField
from django.utils.translation import gettext_lazy as _


def make_published(modeladmin, request, queryset):
    queryset.update(active=True)
make_published.short_description = "Activate elements"

def make_unpublished(modeladmin, request, queryset):
    queryset.update(active=False)
make_unpublished.short_description = "Deactivate elements"

def make_icon_basic(modeladmin, request, queryset):
    queryset.update(category_prototype_id=18)
make_icon_basic.short_description = "Make icon basic"

def make_icon_arrow(modeladmin, request, queryset):
    queryset.update(category_prototype_id=12)
make_icon_arrow.short_description = "Make icon arrow"


class ElementSetting(admin.ModelAdmin):
    actions_selection_counter = True
    list_display = ['title', 'category_prototype', 'light_image', 'dark_image', 'active']
    fields = ('title', 'category_prototype', 'light_image', 'dark_image', 'light_layout', 'dark_layout', 'active')
    actions = [make_published, make_unpublished, make_icon_basic, make_icon_arrow]
    ordering = ['title']
    empty_value_display = '-empty-'
    list_display_links = ('title',)
    list_editable = ('active', 'category_prototype')
    list_filter = ('active', 'category_prototype')
    preserve_filters = False
    save_as = True
    search_fields = ['title']


class DecadeBornListFilter(admin.SimpleListFilter):
    title = _('permissions')
    parameter_name = 'decade'

    def lookups(self, request, model_admin):
        return (
            ('read', _('read permission')),
            ('edit', _('edit permission')),
            ('delete', _('delete permission')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'read':
            permissions = [['read', 'edit', 'delete'], ['read', 'edit'], ['read', 'delete'], ['read'],
                           ['edit', 'read', 'delete'], ['edit', 'read'], ['delete', 'read'],
                           ['edit', 'delete', 'read'], ['delete', 'edit', 'read'], ['delete', 'read', 'edit'],
                           ['read', 'delete', 'edit']]
            return queryset.filter(permission__in=permissions)
        if self.value() == 'edit':
            permissions = [['read', 'edit', 'delete'], ['edit', 'read'], ['edit', 'delete'], ['edit'],
                           ['edit', 'read', 'delete'], ['read', 'edit'], ['delete', 'edit'],
                           ['edit', 'delete', 'read'], ['delete', 'edit', 'read'], ['delete', 'read', 'edit'],
                           ['read', 'delete', 'edit']]
            return queryset.filter(permission__in=permissions)
        if self.value() == 'delete':
            permissions = [['read', 'edit', 'delete'], ['delete', 'read'], ['delete', 'edit'], ['delete'],
                           ['edit', 'read', 'delete'], ['read', 'delete'], ['edit', 'delete'],
                           ['edit', 'delete', 'read'], ['delete', 'edit', 'read'], ['delete', 'read', 'edit'],
                           ['read', 'delete', 'edit']]
            return queryset.filter(permission__in=permissions)


class ShareProjectSetting(admin.ModelAdmin):
    actions_selection_counter = True
    list_display = ['project_id', 'project', 'from_user_email', 'to_user', 'permission', 'all_users']
    ordering = ['project_id']
    list_display_links = ('project_id', 'project')
    list_filter = ('all_users', DecadeBornListFilter)
    preserve_filters = False
    save_as = True
    search_fields = ['project__name', 'project__id', 'from_user__first_name', 'to_user__last_name', 'to_user__email']

    def from_user_email(self, obj):
        return obj.from_user.email
    from_user_email.short_description = 'from_user'

    def to_user_email(self, obj):
        return obj.to_user.email
    to_user_email.short_description = 'to_user'


class CategoryAdmin(admin.ModelAdmin):
    actions_selection_counter = True
    list_display = ['title', 'slug', 'two_in_row']
    ordering = ['id']
    list_filter = ('two_in_row',)
    preserve_filters = False
    save_as = True
    search_fields = ['title', 'slug']


class SettingsAdmin(admin.ModelAdmin):
    list_display = ('slug', 'value')
    # readonly_fields = ('slug',)

    def has_delete_permission(self, request, obj=None):
        return False


class ElementInline(nested_admin.NestedTabularInline):
    model = Element
    extra = 0



class BaseWidthInline(admin.TabularInline):
    model = Prototype.base_width.through
    extra = 1


class ProjectSetting(admin.ModelAdmin):
    actions_selection_counter = True
    list_display = ['id', 'name', 'prototype', 'colors', 'count', 'previewScreenId']
    readonly_fields = ['count']
    list_display_links = ('id', 'name')
    list_filter = ('prototype',)
    preserve_filters = False
    save_as = True
    search_fields = ['id', 'name', 'prototype__device_name', 'user__email']


class ScreenSetting(admin.ModelAdmin):
    actions_selection_counter = True
    list_display = ['id', 'title', 'project', 'width', 'height', 'background_color', 'position', 'styles']
    list_display_links = ('id', 'title')
    list_filter = ('width', 'height')
    preserve_filters = False
    save_as = True
    search_fields = ['id', 'title', 'project__id', 'project__name', 'width', 'height', 'styles']


class PrototypeSetting(admin.ModelAdmin):
    inlines = (
        BaseWidthInline,
    )
    actions_selection_counter = True
    list_display = ['id', 'device_name', 'width', 'height', 'image', 'image_hover']
    list_display_links = ('id', 'device_name')
    list_filter = ('width', 'height')
    preserve_filters = False
    save_as = True
    search_fields = ['id', 'device_name']


class ConstantColorsSetting(admin.ModelAdmin):
    actions_selection_counter = True
    list_display = ['id', 'title', 'dark_value', 'light_value', 'project', 'to_prototype']
    readonly_fields = ['project']
    list_display_links = ('id', 'title')
    list_filter = ('to_prototype',)
    preserve_filters = False
    save_as = True
    search_fields = ['id', 'title', 'project__id', 'project__name', 'prototype__id', 'prototype__device_name']


class UserPermissionSetting(admin.ModelAdmin):
    actions_selection_counter = True
    list_display = ['id', 'user', 'permission', 'last_update']
    list_display_links = ('id', 'user')
    list_filter = ('permission',)
    preserve_filters = False
    save_as = True
    search_fields = ['id', 'user__email', 'last_update']


class ModesSettings(admin.ModelAdmin):
    search_fields = ['id', 'project__id', 'project__name']


class UserAboutSettings(admin.ModelAdmin):
    actions_selection_counter = True
    list_display = ['id', 'user', 'profession', 'framework', 'news', 'theme']
    readonly_fields = ['user']
    ordering = ['profession', 'framework', 'news', 'theme']
    list_display_links = ('id', 'user')
    list_filter = ['profession', 'framework', 'news', 'theme']
    preserve_filters = False
    save_as = True
    search_fields = ['user__email', 'user__id']


admin.site.register(Prototype, PrototypeSetting)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Settings, SettingsAdmin)
admin.site.register(Project, ProjectSetting)
admin.site.register(SharedProject, ShareProjectSetting)
admin.site.register(Element, ElementSetting)
admin.site.register(Screen, ScreenSetting)
admin.site.register(Revision)
admin.site.register(Version)
admin.site.register(BaseWidthPrototype)
admin.site.register(Constant_colors, ConstantColorsSetting)
admin.site.register(ModesState, ModesSettings)
admin.site.register(FigmaUser)
admin.site.register(PasswordReset)
admin.site.register(ClientStrip)
admin.site.register(Price)
admin.site.register(Subscription)
admin.site.register(UserPermission, UserPermissionSetting)
admin.site.register(UserAbout, UserAboutSettings)
admin.site.register(ssoToken)
admin.site.register(FirebaseSettings)
admin.site.register(FirebaseRequest)
