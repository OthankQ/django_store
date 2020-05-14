from django.db import models


class User(models.Model):
    user_id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255)
    phone_number = models.IntegerField(null=True, blank=True)
    # etc = models.CharField(max_length=255)

    def __str__(self):
        return self.user_id


class Item(models.Model):
    item_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    desc = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image_id = models.IntegerField(null=True, blank=True)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class InvoiceStatus(models.Model):
    INVOICE_STATUS = (('cart', 'cart'), ('pending', 'pending'),
                      ('shipped', 'shipped'), ('fulfilled', 'fulfilled'))
    status = models.CharField(
        max_length=10, default="cart", choices=INVOICE_STATUS)

    def __str__(self):
        return self.status


class Invoice(models.Model):
    # INVOICE_STATUS = (('cart', 'cart'),('pending', 'pending'),('shipped', 'shipped'), ('fulfilled', 'fulfilled'))
    invoice_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField('invoice creation date')
    # status = models.CharField(max_length=10, default="cart", choices=INVOICE_STATUS)
    status = models.ForeignKey(InvoiceStatus, on_delete=models.CASCADE)

    # etc = models.CharField(max_length=255)

    def __str__(self):
        return str(self.invoice_id)


class LineItem(models.Model):
    line_item_id = models.AutoField(primary_key=True)
    invoice_id = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    # line_item_name = models.CharField(max_length=255)
    line_item_price = models.DecimalField(
        max_digits=7, decimal_places=2, default=0)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return str(self.line_item_id)
