# Generated by Django 3.2.5 on 2021-08-30 01:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_auto_20210810_1909'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesman',
            name='address',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]