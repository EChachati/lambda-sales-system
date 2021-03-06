# Generated by Django 3.2.5 on 2021-07-20 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_salesman'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identity_card', models.CharField(max_length=15)),
                ('name', models.CharField(max_length=50)),
                ('image', models.ImageField(blank=True, null=True, upload_to='client')),
                ('address', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=15)),
                ('purchases', models.PositiveIntegerField()),
                ('money_spent', models.DecimalField(decimal_places=2, max_digits=12)),
            ],
        ),
    ]
