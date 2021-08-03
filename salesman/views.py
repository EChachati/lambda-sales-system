from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Salesman
from salesman import serializers


class SalesmanViewSet(viewsets.ModelViewSet):
    """
    Manage Salesman in database
    """

    queryset = Salesman.objects.all()
    serializer_class = serializers.SalesmanSerializer
