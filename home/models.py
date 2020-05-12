from django.db import models

# Create your models here.

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    phone_number = models.IntegerField()
    etc = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Item(models.Model):
    item_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    desc = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image_id = models.IntegerField()
    stock = models.IntegerField()

    def __str__(self):
        return self.item_id


class Invoice(models.Model):
    invoice_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField('invoice creation date')
    status = models.CharField(max_length=255)
    etc = models.CharField(max_length=255)

    def __str__(self):
        return self.invoice_id      


class LineItem(models.Model):
    line_item_id = models.AutoField(primary_key=True)
    invoice_id = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    line_item_name = models.CharField(max_length=255)
    quantity = models.IntegerField()

    def __str__(self):
        return self.line_item_name