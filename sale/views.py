from rest_framework import viewsets

from core.models import Sale, ProductSale, Salesman, Client, SalesmanIndicators
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

        income = request.data['income']

        salesman = Salesman.objects.get(pk=request.data['salesman'])

        salesman_indicator = SalesmanIndicators.objects.get(pk=salesman)

        salesman_indicator.purchases += 1
        salesman_indicator.money_generated += decimal.Decimal(income)

        if decimal.Decimal(income) > salesman_indicator.biggest_sale.income or not salesman_indicator.biggest_sale:
            salesman_indicator.biggest_sale = instance

        salesman_indicator.save()

        client = Client.objects.get(pk=request.data['client'])
        client.purchases += 1
        client.money_spent += decimal.Decimal(income)
        client.save()
        return instance


class ProductSaleViewSet(viewsets.ModelViewSet):
    """
    Manage Product Sales in Database
    """
    queryset = ProductSale.objects.all()
    serializer_class = serializers.ProductSaleSerializer
