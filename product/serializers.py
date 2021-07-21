from rest_framework import serializers

from core.models import Product, Category, Barcode


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category Object
    """
    class Meta:
        model = Category
        fields = ('id', 'name')
        read_only_fields = ('id',)
