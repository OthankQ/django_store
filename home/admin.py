from django.contrib import admin

# Register your models here.
from .models import User, Item, Invoice, LineItem

class InvoiceInline(admin.TabularInline):
    model = Invoice
    extra = 3

# class LineItemInline(admin.TabularInline):
#     model = LineItem
#     extra = 3

class UserAdmin(admin.ModelAdmin):
    fieldsets = [('General Information', {'fields': ('name', 'phone_number', 'password')}),]
    inlines = [InvoiceInline]

admin.site.register(User, UserAdmin)