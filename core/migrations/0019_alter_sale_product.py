# Generated by Django 3.2.5 on 2021-08-04 00:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_barcode_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='product',
            field=models.ManyToManyField(blank=True, through='core.ProductSale', to='core.Product'),
        ),
    ]
