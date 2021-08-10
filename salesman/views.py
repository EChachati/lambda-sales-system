from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Salesman, SalesmanIndicators
from salesman import serializers


class SalesmanViewSet(viewsets.ModelViewSet):
    """
    Manage Salesman in database
    """

    queryset = Salesman.objects.all()
    serializer_class = serializers.SalesmanSerializer

    def create(self, request):
        """
        Create SalesmanIndicators instance
        """
        instance = super().create(request)
        salesman = Salesman.objects.get(pk=instance.data['id'])

        indicators = SalesmanIndicators.objects.create(salesman=salesman)
        indicators.save()
        return instance


class SalesmanIndicatorsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SalesmanIndicators.objects.all()
    serializer_class = serializers.SalesmanIndicatorsSerializer
