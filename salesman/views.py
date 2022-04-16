from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response


from core.models import Salesman, SalesmanIndicators
from core.utils import upload_image

from salesman import serializers


class SalesmanViewSet(viewsets.ModelViewSet):
    """
    Manage Salesman in database
    """

    queryset = Salesman.objects.all()
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


class SalesmanIndicatorsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SalesmanIndicators.objects.all()
    serializer_class = serializers.SalesmanIndicatorsSerializer


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
