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


class SalesmanAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'identity_card')


class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'identity_card', 'purchases', 'money_spent')
    ordering = ('-name', )


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'presentation',
                    'cost', 'price_1', 'price_2', 'price_3')
    ordering = ('-name',)


class BarcodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'product')


class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', _('client'), _('salesman'), _('income'), _('date'))


class ProductSaleAdmin(admin.ModelAdmin):
    list_display = ('sale', 'product', 'quantity', 'income')
    ordering = ('-sale', )


# admin.site.register(User, UserAdmin)
admin.site.register(Salesman, SalesmanAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Barcode, BarcodeAdmin)
admin.site.register(Sale, SaleAdmin)
admin.site.register(ProductSale, ProductSaleAdmin)
admin.site.register(SalesmanIndicators)
