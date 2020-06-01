from django.contrib import admin

# Register your models here.
from .models import UserAdditionalInfo, Item, Invoice, LineItem, Message
from django.contrib.auth.admin import UserAdmin


class InvoiceInline(admin.TabularInline):
    model = Invoice
    extra = 1


class LineItemInline(admin.TabularInline):
    model = LineItem
    extra = 3


class UserAdditionalInfoAdmin(admin.ModelAdmin):
    fieldsets = [('General Information', {'fields': (
        'user', 'name', 'phone_number', 'image')}), ]


class InvoiceAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ('date', 'status', 'user')})]
    inlines = [LineItemInline]


class ItemAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ('name', 'desc', 'price', 'stock', 'image')})]


class MessageAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ('user', 'line_item', 'message_body', 'date_created', 'image')})]


# admin.site.register(User, UserAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(UserAdditionalInfo, UserAdditionalInfoAdmin)
