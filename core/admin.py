from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

"""
In order to make a Django project translatable, you have to add a minimal
number of hooks to your Python code and templates. These hooks are called
translation strings. They tell Django: “This text should be translated into the
end user’s language, if a translation for this text is available in that
language.” It’s your responsibility to mark translatable strings; the system
can only translate strings it knows about
"""
from django.utils.translation import gettext as _


from core.models import *


class UserAdmin(BaseUserAdmin):
    """
    User Model displayed in admin
    """
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {
            "fields": (
                _('email'),
                _('password')
            ),
        }),

        (_('Personal Information'), {
            "fields": (
                _('name'),
                _('identity_card')
            )
        }),
        (_('Permissions'), {
            "fields": (
                _('is_active'),
                _('is_staff'),
                _('is_superuser')
            )
        }),
        (_('Important Dates'), {
            "fields": (
                _('last_login'),
            )
        })
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }
        ),
    )


admin.site.register(User, UserAdmin)
