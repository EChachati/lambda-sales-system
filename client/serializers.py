from rest_framework import serializers

from core.models import Client


class ClientSerializer(serializers.ModelSerializer):
    """
    Serializer for Client Object
    """
    class Meta:
        model = Client
        fields = (
            'id',
            'name',
            'identity_card',
            'image',
            'address',
            'phone',
            'purchases',
            'money_spent'
        )
