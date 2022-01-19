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

    barcode = CodeSerializer(many=True, read_only=True)
    #category = CategorySerializer()

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('id',)

    def to_representation(self, product):
        """
        Adding Category Detail to Serializer
        """
        data = super().to_representation(product)
        category = CategorySerializer(product.category)
        data['category'] = category.data
        data['image'] = product.image.name
        return data
