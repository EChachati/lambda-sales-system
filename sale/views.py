from rest_framework import viewsets

from core.models import Sale, ProductSale
from sale import serializers


class SaleViewSet(viewsets.ModelViewSet):
    """
    Manage Sales in Database
    """
    queryset = Sale.objects.all()
    serializer_class = serializers.SaleSerializer
