from rest_framework import serializers
from core.models import Sale, ProductSale


class ProductSaleSerializer(serializers.ModelSerializer):
    """
    Product-Sale Serializer
    """
    class Meta:
        model = ProductSale
        fields = ('id', 'product', 'sale', 'quantity', 'income')


class SaleSerializer(serializers.ModelSerializer):
    """
    Serializer for Sale
    """

    product = ProductSaleSerializer(many=True)

    class Meta:
        model = Sale
        fields = (
            'id',
            'salesman',
            'client',
            'income',
            'product',
            'description',
            'date'
        )
