from rest_framework import serializers

from core.models import Product, Category, Barcode


class BarcodeSerializer(serializers.ModelSerializer):
    """
    Barcodes per Product
    """
    class Meta:
        model = Barcode
        fields = ('code', 'product')


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category Object
    """
    class Meta:
        model = Category
        fields = ('id', 'name')
        read_only_fields = ('id',)


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product Object
    """
    barcode = BarcodeSerializer(many=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'category', 'description', 'cost',
                  'price_1', 'price_2', 'price_3', 'brand', 'image', 'barcode')
        read_only_fields = ('id',)
