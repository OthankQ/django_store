# Generated by Django 3.0.6 on 2020-05-19 18:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_item_user_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item',
            old_name='user_id',
            new_name='user',
        ),
    ]
