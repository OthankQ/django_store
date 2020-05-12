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
    fieldsets = [('Username', {'fields': ['name']}), ('Phone', {'fields': ['phone_number']}),]
    inlines = [InvoiceInline]

admin.site.register(User, UserAdmin)