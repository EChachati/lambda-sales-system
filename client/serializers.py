from rest_framework import serializers

from core.models import Client, ClientIndicator


class ClientSerializer(serializers.ModelSerializer):
    """
    Serializer for Client Object
    """
    class Meta:
        model = Client
        fields = '__all__'


class ClientIndicatorSerializer(serializers.ModelSerializer):
    """
    Serializer for Client indicator Object
    """
    class Meta:
        model = ClientIndicator
        fields = '__all__'
