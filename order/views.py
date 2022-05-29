from rest_framework import viewsets, status
from rest_framework.generics import ListCreateAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpRequest
from moneyed import Money

from core.models import Order, ProductOrder, OrderSale, SalesmanIndicators, ClientIndicator, Salesman, Client, Sale, Product, ProductSale
from order import serializers
from sale.views import SaleViewSet


class OrderViewSet(viewsets.ModelViewSet):
    """
    Manage Orders in Database
    """
    queryset = Order.objects.all().order_by('-date', '-id')
    serializer_class = serializers.OrderSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        It takes a request object and a queryset, and returns a queryset that has been filtered
        according to the query parameters in the request
        :return: The queryset is being returned.
        """
        return apply_query_filters(self.request, self.queryset)

    def create(self, request, *args, **kwargs):
        """
        It creates a sale, updates the salesman and client indicators, and returns the sale.

        :param request: The request object
        :return: The instance of the object that was created.
        """
        instance = super().create(request)

        order = Order.objects.get(pk=instance.data['id'])

        sale = Sale.objects.create(
            id=order.id,
            salesman=order.salesman,
            client=order.client,
            date=order.date,
            income=order.income,
        )
        sale.save()

        salesman = Salesman.objects.get(pk=request.data['salesman'])
        client = Client.objects.get(pk=request.data['client'])
        income = Money(request.data['income'], 'USD')

        c_indicator = ClientIndicator.objects.get(pk=client)
        s_indicator = SalesmanIndicators.objects.get(pk=salesman)

        s_indicator.purchases += 1
        s_indicator.money_generated += income

        if not s_indicator.biggest_sale or income > s_indicator.biggest_sale.income:
            s_indicator.biggest_sale = sale

        c_indicator.purchases += 1
        c_indicator.money_generated += income

        if not c_indicator.biggest_sale or income > c_indicator.biggest_sale.income:
            c_indicator.biggest_sale = sale

        s_indicator.save()
        c_indicator.save()

        order_sale = OrderSale.objects.create(
            order=order, sale=sale)
        return instance


class CreateProductOrderAPIView(ListCreateAPIView):
    """
    Create multiple products with one Post using a list
    """
    queryset = ProductOrder.objects.all()
    serializer_class = serializers.ProductOrderSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        """
        It creates a ProductOrder object for each item in the request.data list

        :param request: The request object
        :return: A list of ProductOrder objects
        """
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
            data['order'] = Order.objects.get(pk=data['sale'])
            ps_obj = ProductOrder.objects.create(order=data['order'], product=data['product'], income=data['income'], quantity=data['quantity'])
            ps = ProductSale.objects.create(sale=data['sale'], product=data['product'], income=data['income'], quantity=data['quantity'])
            ps.save()
            ps_created.append(ps_obj.id)

        results = ProductOrder.objects.filter(id__in=ps_created)
        output_serializer = serializers.ProductOrderSerializer(
            results, many=True)
        data = output_serializer.data[:]
        return Response(data, status=status.HTTP_201_CREATED)
