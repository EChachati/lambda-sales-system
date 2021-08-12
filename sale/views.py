from rest_framework import viewsets

from core.models import Sale, ProductSale, Salesman, Client, SalesmanIndicators, ClientIndicator
from sale import serializers

import decimal


class SaleViewSet(viewsets.ModelViewSet):
    """
    Manage Sales in Database
    """
    queryset = Sale.objects.all()
    serializer_class = serializers.SaleSerializer

    def create(self, request):
        """
        Update values in client and salesman models
        """
        instance = super().create(request)

        salesman = Salesman.objects.get(pk=request.data['salesman'])
        client = Client.objects.get(pk=request.data['client'])
        sale = Sale.objects.get(pk=instance.data['id'])
        income = request.data['income']

        c_indicator = ClientIndicator.objects.get(pk=client)
        s_indicator = SalesmanIndicators.objects.get(pk=salesman)

        s_indicator.purchases += 1
        s_indicator.money_generated += decimal.Decimal(income)

        if not s_indicator.biggest_sale or decimal.Decimal(income) > s_indicator.biggest_sale.income:
            s_indicator.biggest_sale = sale

        c_indicator.purchases += 1
        c_indicator.money_generated += decimal.Decimal(income)

        if not c_indicator.biggest_sale or decimal.Decimal(income) > c_indicator.biggest_sale.income:
            c_indicator.biggest_sale = sale

        s_indicator.save()
        c_indicator.save()

        return instance


class ProductSaleViewSet(viewsets.ModelViewSet):
    """
    Manage Product Sales in Database
    """
    queryset = ProductSale.objects.all()
    serializer_class = serializers.ProductSaleSerializer
