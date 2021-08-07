from rest_framework import serializers

from core.models import Product, Category, Barcode


class BarcodeSerializer(serializers.ModelSerializer):
    """
    All Barcodes per Product
    """
    class Meta:
        model = Barcode
        fields = ('id', 'product', 'description', 'code')


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

    class CodeSerializer(serializers.ModelSerializer):
        """
        Barcode Serializer just display the code and description, used in ProductSerializer
        """
        class Meta:
            model = Barcode
            fields = ('description', 'code',)

    barcode = CodeSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = '__all__'
#        ('id', 'name', 'category', 'description', 'cost', 'price_1', 'price_2', 'price_3', 'brand', 'image', 'barcode')
        read_only_fields = ('id',)
