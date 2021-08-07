# Generated by Django 3.2.5 on 2021-08-04 00:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_alter_sale_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productsale',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product', to='core.product'),
        ),
        migrations.AlterField(
            model_name='productsale',
            name='sale',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sale', to='core.sale'),
        ),
        migrations.AlterField(
            model_name='sale',
            name='product',
            field=models.ManyToManyField(blank=True, through='core.ProductSale', to='core.Product'),
        ),
    ]
