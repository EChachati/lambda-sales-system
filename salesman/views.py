from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

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
