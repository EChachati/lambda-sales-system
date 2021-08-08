from rest_framework import viewsets

from core.models import Sale, ProductSale, Salesman, Client
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
        salesman.purchases += 1
        salesman.money_generated += decimal.Decimal(income)
        salesman.save()

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
