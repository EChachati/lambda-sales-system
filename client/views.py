from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Client
from client import serializers


class ClientViewSet(viewsets.ModelViewSet):
    """
    Manage Client in database
    """
    queryset = Client.objects.all()
    serializer_class = serializers.ClientSerializer
