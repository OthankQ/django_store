from django.contrib import admin

# Register your models here.
from .models import User, Item, Invoice, LineItem

class InvoiceInline(admin.TabularInline):
    model = Invoice
    extra = 3

class LineItemInline(admin.TabularInline):
    model = LineItem
    extra = 3

class UserAdmin(admin.ModelAdmin):
    fieldsets = [('General Information', {'fields': ('name', 'phone_number', 'password')}),]
    inlines = [InvoiceInline]

class InvoiceAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ('user_id', 'date', 'status')})]    
    inlines = [LineItemInline]

class ItemAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ('name', 'desc', 'price', 'stock', 'image_id')})]

admin.site.register(User, UserAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Item, ItemAdmin)