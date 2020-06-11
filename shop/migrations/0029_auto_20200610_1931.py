# Generated by Django 3.0.6 on 2020-06-10 23:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0028_useradditionalinfo_display_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useradditionalinfo',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='users/'),
        ),
        migrations.CreateModel(
            name='ItemImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='item/')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.Item')),
            ],
        ),
    ]
