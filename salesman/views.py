from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response


from core.models import Salesman, SalesmanIndicators
from core.utils import upload_image, apply_query_filters, load_model, predict

from salesman.ia import *
from salesman import serializers


class SalesmanViewSet(viewsets.ModelViewSet):
    """
    Manage Salesman in database
    """

    queryset = Salesman.objects.all().order_by('name')
    serializer_class = serializers.SalesmanSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        """
        Create SalesmanIndicators instance
        """
        instance = super().create(request)
        salesman = Salesman.objects.get(pk=instance.data['id'])

        if salesman.image:
            salesman.image = upload_image(salesman.image)
        else:
            salesman.image = 'https://i.ibb.co/JypJ3Ny/pngaaa-com-5015561.png'

        instance.data['image'] = salesman.image.name
        salesman.save()

        indicators = SalesmanIndicators.objects.create(salesman=salesman)
        indicators.save()
        return instance

    def get_queryset(self):
        return apply_query_filters(self.request, self.queryset)


class SalesmanIndicatorsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SalesmanIndicators.objects.all()
    serializer_class = serializers.SalesmanIndicatorsSerializer

    def get_queryset(self):
        return apply_query_filters(self.request, self.queryset)


class SalesmanMe(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        If the user logged is a Salesman, return his data
        """
        if request.user.type in ['SALESMAN', 'SALESMAN_AND_CLIENT']:
            salesman = Salesman.objects.get(
                identity_card=request.user.identity_card)
            return Response(SalesmanIndicators.objects.get(
                salesman=salesman).to_dict())
        else:
            print('ERROR: User is not a salesman')
            return Response(
                {'Error': 'User is not a Salesman'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def patch(self, request, format=None):
        """
        Check if the user is a salesman, then update his data with the request data except for the identity_card
        """

        if 'identity_card' in request.data.keys() and request.data['identity_card'] != request.user.identity_card:
            return Response(
                {'Error': 'You can not change your identity_card'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.user.type in ['SALESMAN', 'SALESMAN_AND_CLIENT']:
            salesman = Salesman.objects.get(
                identity_card=request.user.identity_card)

            if 'image' in request.data.keys():
                url = upload_image(request.data['image'])
                image = request.data.pop('image')
                salesman.image = url
                salesman.save()

            serializer = serializers.SalesmanSerializer(
                salesman, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(salesman.to_dict())
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            print('ERROR: User is not a salesman')
            return Response(
                {'Error': 'User is not a Salesman'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, format=None):
        """
        Check if the user is a salesman, then delete his data
        """

        if request.user.type in ['SALESMAN', 'SALESMAN_AND_CLIENT']:
            salesman = Salesman.objects.get(
                identity_card=request.user.identity_card)
            salesman.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            print('ERROR: User is not a salesman')
            return Response(
                {'Error': 'User is not a Salesman'},
                status=status.HTTP_400_BAD_REQUEST
            )


class IAView(APIView):
    def post(self, request, *args, **kwargs):
        model_type = 'income' if bool(request.data['income']) else 'count'

        model = load_model(f"salesman_{model_type}_per_month_model")
        if not model:
            model = train_model(income=bool(request.data['income']))

        data = get_grouped_data()
        data = data[data['salesman_id'] == request.data['salesman_id']]
        #data = data[(data['year'] == 2022) & (data['month'] == 1)]
        print(data)
        data.drop(columns=['year', 'name', 'sales_next_month',
                  'sales_next_month_count'], inplace=True)

        #import pdb
        # pdb.set_trace()

        imputer = SimpleImputer().fit_transform(data)
        ret = model.predict(imputer)

        return Response(ret, status=status.HTTP_200_OK)


class StatisticsView(APIView):
    def post(self, request, *args, **kwargs):
        salesman_id = request.data.get('salesman_id')
        type = request.data['type']

        if type not in ['category', 'product', 'client']:
            return Response({'error': 'Invalid type dejate de mamadas fran pasa uno de estos tres ["category", "product", "client"]'}, status=status.HTTP_400_BAD_REQUEST)

        if type == 'category':
            data = sales_realized_per_category(salesman_id)
        elif type == 'product':
            data = sales_realized_per_product(salesman_id)
        elif type == 'client':
            data = sales_realized_per_client(salesman_id)

        return Response(data, status=status.HTTP_200_OK)
