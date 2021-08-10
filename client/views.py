from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Client, ClientIndicator
from client import serializers


class ClientViewSet(viewsets.ModelViewSet):
    """
    Manage Client in database
    """
    queryset = Client.objects.all()
    serializer_class = serializers.ClientSerializer

    def create(self, request):
        instance = super().create(request)
        client = Client.objects.get(pk=instance.data['id'])
        obj = ClientIndicator.objects.create(client=client)
        obj.save()
        return instance


class ClientIndicatorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Get Client Indicators in Database
    """
    queryset = ClientIndicator.objects.all()
    serializer_class = serializers.ClientIndicatorSerializer
