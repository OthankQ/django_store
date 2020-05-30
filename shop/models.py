from django.db import models
from django.contrib.auth.models import User


class UserAdditionalInfo(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255)
    phone_number = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.user_id


class Item(models.Model):
    item_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    desc = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    # image_id = models.IntegerField(blank=True, default=0)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class InvoiceStatus(models.Model):
    INVOICE_STATUS = (('cart', 'cart'), ('paid', 'paid'),
                      ('completed', 'completed'))
    status = models.CharField(
        max_length=10, default="cart", choices=INVOICE_STATUS)

    def __str__(self):
        return self.status


class Invoice(models.Model):
    # INVOICE_STATUS = (('cart', 'cart'),('pending', 'pending'),('shipped', 'shipped'), ('fulfilled', 'fulfilled'))
    invoice_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField('invoice creation date')
    # status = models.CharField(max_length=10, default="cart", choices=INVOICE_STATUS)
    status = models.ForeignKey(InvoiceStatus, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.invoice_id)


class LineItemStatus(models.Model):
    LINE_ITEM_STATUS = (('in cart', 'in cart'), ('pending', 'pending'),
                        ('in locker', 'in locker'), ('picked up', 'picked up'))
    status = models.CharField(
        max_length=10, default="in cart", choices=LINE_ITEM_STATUS)

    def __str__(self):
        return self.status


class LineItem(models.Model):
    line_item = models.AutoField(primary_key=True)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    # line_item_name = models.CharField(max_length=255)
    line_item_price = models.DecimalField(
        max_digits=15, decimal_places=2, default=0)
    quantity = models.IntegerField(default=0)
    status = models.ForeignKey(
        LineItemStatus, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.line_item)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
    # cleared = models.BooleanField(default=False)
    notification_body = models.CharField(max_length=255)
    line_item_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.notification_body


class Messages(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    line_item = models.ForeignKey(LineItem, on_delete=models.CASCADE)
    message_body = models.CharField(max_length=255)
    date_created = models.DateTimeField('message creation date')
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.message_body
