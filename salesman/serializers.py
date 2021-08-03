from rest_framework import serializers

from core.models import Salesman


class SalesmanSerializer(serializers.ModelSerializer):
    """
    Serializer for Salesman Object
    """
    class Meta:
        model = Salesman
        fields = (
            'id',
            'name',
            'identity_card',
            'phone_1',
            'phone_2',
            'image',
            'purchases',
            'money_generated',
            'biggest_sell'
        )
