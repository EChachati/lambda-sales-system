# Generated by Django 3.2.5 on 2021-08-03 18:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20210802_2117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='barcode',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='barcode', to='core.product'),
        ),
    ]
