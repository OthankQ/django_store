from django.contrib import admin

# Register your models here.
from .models import User, Item, Invoice, LineItem
from django.contrib.auth.admin import UserAdmin

class InvoiceInline(admin.TabularInline):
    model = Invoice
    extra = 1

class LineItemInline(admin.TabularInline):
    model = LineItem
    extra = 3

class UserAdmin(admin.ModelAdmin):
    fieldsets = [('General Information', {'fields': ('user_id', 'name', 'phone_number', 'password')}),]
    inlines = [InvoiceInline]

class InvoiceAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ('user_id', 'date', 'status')})]    
    inlines = [LineItemInline]

class ItemAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ('name', 'desc', 'price', 'stock', 'image_id')})]


admin.site.register(User, UserAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Item, ItemAdmin)