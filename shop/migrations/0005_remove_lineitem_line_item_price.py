# Generated by Django 3.0.6 on 2020-05-13 15:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_auto_20200513_1121'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lineitem',
            name='line_item_price',
        ),
    ]
