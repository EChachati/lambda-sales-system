# Generated by Django 3.2.5 on 2022-02-25 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_alter_client_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='id',
            field=models.CharField(max_length=50, primary_key=True, serialize=False),
        ),
    ]