from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from sklearn.impute import SimpleImputer

from core.models import Client, ClientIndicator
from core.utils import upload_image, apply_query_filters, predict, load_model
from client import serializers
from client.ia import *


class ClientViewSet(viewsets.ModelViewSet):
    """
    Manage Client in database
    """
    queryset = Client.objects.all().order_by('name')
    serializer_class = serializers.ClientSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return apply_query_filters(self.request, self.queryset)

    def create(self, request):
        """
        Create a New Client
        """
        instance = super().create(request)
        client = Client.objects.get(pk=instance.data['id'])

        if client.image:
            client.image = upload_image(client.image)
        else:
            client.image = 'https://i.ibb.co/XF7qJN4/img-552555.png'

        instance.data['image'] = client.image.name
        client.save()
        obj = ClientIndicator.objects.create(client=client)
        obj.save()
        return instance


class ClientIndicatorViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = ClientIndicator.objects.all()
    serializer_class = serializers.ClientIndicatorSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        It takes a request object and a queryset, and returns a queryset that has been filtered
        according to the query parameters in the request
        :return: The queryset is being returned.
        """
        return apply_query_filters(self.request, self.queryset)


class IAView(APIView):
    def post(self, request, *args, **kwargs):
        model_type = 'income' if bool(request.data['income']) else 'count'

        model = load_model(f"client_{model_type}_per_month_model")

        if not model:
            model = train_model(income=bool(request.data['income']))

        data = get_grouped_data()
        data = data[data['client_id'] == request.data['client_id']]
        data = data[(data['year'] == 2022) & (data['month'] == 1)]

        data.drop(columns=['year', 'name', 'sales_next_month',
                  'sales_next_month_count'], inplace=True)

        imputer = SimpleImputer().fit_transform(data)
        ret = model.predict(imputer)

        return Response(ret, status=status.HTTP_200_OK)


class StatisticsView(APIView):
    def post(self, request, *args, **kwargs):
        client_id = request.data.get('client_id')
        type = request.data['type']
        if type not in ['category', 'product', 'salesman']:
            return Response({'error': 'Invalid type dejate de mamadas fran pasa uno de estos tres ["category", "product", "salesman"]'}, status=status.HTTP_400_BAD_REQUEST)

        if type == 'category':
            data = sales_realized_per_category(client_id)
        elif type == 'product':
            data = sales_realized_per_product(client_id)
        elif type == 'salesman':
            data = sales_realized_per_salesman(client_id)

        return Response(data, status=status.HTTP_200_OK)
