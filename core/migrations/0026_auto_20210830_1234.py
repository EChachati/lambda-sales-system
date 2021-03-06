# Generated by Django 3.2.5 on 2021-08-30 16:34

from django.db import migrations
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_alter_productsale_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='cost_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('VES', 'Bolivar Venezolano'), ('USD', 'Dolar')], default='USD', editable=False, max_length=3),
        ),
        migrations.AddField(
            model_name='product',
            name='price_1_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('VES', 'Bolivar Venezolano'), ('USD', 'Dolar')], default='USD', editable=False, max_length=3),
        ),
        migrations.AddField(
            model_name='product',
            name='price_2_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('VES', 'Bolivar Venezolano'), ('USD', 'Dolar')], default='USD', editable=False, max_length=3),
        ),
        migrations.AddField(
            model_name='product',
            name='price_3_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('VES', 'Bolivar Venezolano'), ('USD', 'Dolar')], default='USD', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='product',
            name='cost',
            field=djmoney.models.fields.MoneyField(decimal_places=2, default_currency='USD', max_digits=12),
        ),
        migrations.AlterField(
            model_name='product',
            name='price_1',
            field=djmoney.models.fields.MoneyField(decimal_places=2, default_currency='USD', max_digits=12),
        ),
        migrations.AlterField(
            model_name='product',
            name='price_2',
            field=djmoney.models.fields.MoneyField(decimal_places=2, default_currency='USD', max_digits=12),
        ),
        migrations.AlterField(
            model_name='product',
            name='price_3',
            field=djmoney.models.fields.MoneyField(decimal_places=2, default_currency='USD', max_digits=12),
        ),
    ]
