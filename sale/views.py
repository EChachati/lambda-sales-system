from rest_framework import viewsets, status
from rest_framework.settings import api_settings
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Sale, ProductSale, Salesman, Client, SalesmanIndicators, ClientIndicator, Product
from core.utils import apply_query_filters

from sale import serializers
from moneyed import Money
from sale.ia import load_model, train_model, predict


class SaleViewSet(viewsets.ModelViewSet):
    """
    Manage Sales in Database
    """
    queryset = Sale.objects.all().order_by('-date', '-id')
    serializer_class = serializers.SaleSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return apply_query_filters(self.request, self.queryset)

    def create(self, request):
        """
        Update values in client and salesman models
        """
        instance = super().create(request)

        salesman = Salesman.objects.get(pk=request.data['salesman'])
        client = Client.objects.get(pk=request.data['client'])
        sale = Sale.objects.get(pk=instance.data['id'])
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

        return instance


class CreateProductSaleAPIView(ListCreateAPIView):
    """
    Create multiple products with one Post using a list
    """
    queryset = ProductSale.objects.all()
    serializer_class = serializers.ProductSaleSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

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


class GetSalesBySaleman(ListAPIView):
    """
    Get All sales made by a salesman
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def get_queryset(self):
        return apply_query_filters(self.request, self.queryset)

    def list(self, request, *args, **kwargs):
        salesman_id = kwargs['pk']
        salesman = Salesman.objects.get(pk=salesman_id)
        sales = Sale.objects.raw(
            f"SELECT x.* FROM public.core_sale x WHERE salesman_id = {salesman_id}")
        pdb.set_trace()
        sales = [s.to_dict() for s in sales]
        serializer = serializers.SaleSerializer(sales, many=True)
        return Response(serializer.data)


class IAView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        time_range = 'month' if bool(request.data['month']) else 'year'
        model_type = 'income' if bool(request.data['income']) else 'count'
        group_by = request.data['group_by']  # month, year or None

        model = load_model(
            f"sale_{model_type}_{time_range}_grouped_by_{group_by}_model")

        if not model:
            model = train_model(
                month=bool(request.data['month']),
                income=bool(request.data['income']),
                group_by=request.data['group_by']
            )

        count = [595, 872, 777, 710, 739, 745, 876, 816, 908, 1114, 1106, 838]
        income = [158706.08, 257297.47, 192503.59, 206944.43, 166545.74, 166283.13,
                  158943.72, 138120.65, 175135.81, 279933.26, 272847.04, 222096.95]

        # for test use month=true, income=true, group_by=month

        predictions = predict(model, count, income)

        return Response(predictions)
