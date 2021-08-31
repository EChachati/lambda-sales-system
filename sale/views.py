from rest_framework import viewsets, status
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from core.models import Sale, ProductSale, Salesman, Client, SalesmanIndicators, ClientIndicator, Product
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


class CreateProductSaleAPIView(ListCreateAPIView):
    """
    Create multiple products with one Post using a list
    """
    queryset = ProductSale.objects.all()
    serializer_class = serializers.ProductSaleSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, many=isinstance(request.data, list))
        ps_created = []
        for data in request.data:
            if not (
                'product' in data.keys() and data['product']
                and 'sale' in data.keys() and data['sale']
                    and 'income' in data.keys() and data['income']):
                return Response(request.data, status=status.HTTP_400_BAD_REQUEST)

            data['product'] = Product.objects.get(pk=data['product'])
            data['sale'] = Sale.objects.get(pk=data['sale'])
            ps_obj = ProductSale.objects.create(**data)
            ps_created.append(ps_obj.id)

        results = ProductSale.objects.filter(id__in=ps_created)
        output_serializer = serializers.ProductSaleSerializer(
            results, many=True)
        data = output_serializer.data[:]
        return Response(data, status=status.HTTP_201_CREATED)
