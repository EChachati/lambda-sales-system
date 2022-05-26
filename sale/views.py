from rest_framework import viewsets, status
from rest_framework.settings import api_settings
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Sale, ProductSale, Salesman, Client, SalesmanIndicators, ClientIndicator, Product
from core.utils import apply_query_filters, load_model, predict
from django.db.models import Max

from sale import serializers
from moneyed import Money
from sale.ia import train_model, get_grouped_data
import pandas as pd
from datetime import datetime


class SaleViewSet(viewsets.ModelViewSet):
    """
    Manage Sales in Database
    """
    queryset = Sale.objects.all().order_by('-date', '-id')
    serializer_class = serializers.SaleSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        It takes a request object and a queryset, and returns a queryset that has been filtered
        according to the query parameters in the request
        :return: The queryset is being returned.
        """
        return apply_query_filters(self.request, self.queryset)

    def create(self, request):
        """
        It creates a sale, updates the salesman and client indicators, and returns the sale.

        :param request: The request object
        :return: The instance of the object that was created.
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
        """
        It creates a ProductSale object for each item in the request.data list

        :param request: The request object
        :return: A list of ProductSale objects
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
            ps_obj = ProductSale.objects.create(**data)
            ps_created.append(ps_obj.id)

        results = ProductSale.objects.filter(id__in=ps_created)
        output_serializer = serializers.ProductSaleSerializer(
            results, many=True)
        data = output_serializer.data[:]
        return Response(data, status=status.HTTP_201_CREATED)


class GetSalesBySaleman(ListAPIView):
    """It gets all the sales from a salesman and returns them as a list of dictionaries"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def get_queryset(self):
        """
        It takes a request object and a queryset, and returns a queryset that has been filtered
        according to the query parameters in the request
        :return: The queryset is being returned.
        """
        return apply_query_filters(self.request, self.queryset)

    def list(self, request, *args, **kwargs):
        """
        It gets all the sales from a salesman and returns them as a list of dictionaries

        :param request: The request object
        :return: A list of sales made by a salesman.
        """
        salesman_id = kwargs['pk']
        salesman = Salesman.objects.get(pk=salesman_id)
        sales = Sale.objects.raw(
            f"SELECT x.* FROM public.core_sale x WHERE salesman_id = {salesman_id}")

        sales = [s.to_dict() for s in sales]
        serializer = serializers.SaleSerializer(sales, many=True)
        return Response(serializer.data)


class IAView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
        It takes the request data, loads the model, gets the data, and returns the predictions

        :param request: the request object
        :param format: The format of the response
        :return: The predictions for the next year.
        """
        time_range = 'month' if bool(request.data['by_month']) else 'year'
        model_type = 'income' if bool(request.data['income']) else 'count'

        # month, year or None
        group_by = request.data['group_by'] if 'group_by' in request.data.keys(
        ) else None

        model = load_model(
            f"sale_{model_type}_{time_range}_grouped_by_{group_by}_model")

        if not model:
            model = train_model(
                month=bool(request.data['by_month']),
                income=bool(request.data['income']),
                group_by=group_by
            )
        df_dict = get_grouped_data(to_dict=True)
        if group_by == 'month':
            # To get income and count for every month in 2021
            predict_df = pd.DataFrame(df_dict[2021])

            income = predict_df.iloc[0].tolist()
            count = predict_df.iloc[1].tolist()
            predictions = predict(model, income=income,
                                  count=count, month=list(range(1, 13)))
            months_names = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            d = {}
            for i in range(12):
                d[months_names[i]] = predictions[i]
            return Response(d)
        else:  # NONE
            if time_range == 'month':
                month = request.data['month']
                actual_month = 2
                year = datetime.now().year
                count = df_dict[year][actual_month]['count']
                income = df_dict[year][actual_month]['income']
                predictions = predict(model, [count], [income], [month])
            else:
                predict_df = pd.DataFrame(df_dict[2021])
                income = sum(predict_df.iloc[0].tolist())
                count = sum(predict_df.iloc[1].tolist())
                predictions = predict(model, count=[count], income=[income])
        return Response(predictions)


class StatisticView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        year = request.data['year']
        data = get_grouped_data(to_dict=True)
        data = data[year]
        data_list = []
        month = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        for key, value in data.items():
            value['name'] = month[int(key) - 1]
            data_list.append(value)
        return Response(data_list)


class GetBiggestSale(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        sale = Sale.objects.latest('income')
        return Response(sale.id)
