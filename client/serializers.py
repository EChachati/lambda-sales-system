from rest_framework import serializers

from core.models import Client, ClientIndicator


class ClientSerializer(serializers.ModelSerializer):
    """
    Serializer for Client Object
    """
    class Meta:
        model = Client
        fields = '__all__'

    def to_representation(self, instance):
        """
        Override to_representation to add image field
        """
        representation = super().to_representation(instance)
        representation['image'] = instance.image.name
        return representation


class ClientIndicatorSerializer(serializers.ModelSerializer):
    """
    Serializer for Client indicator Object
    """
    class Meta:
        model = ClientIndicator
        fields = '__all__'

    def to_representation(self, value):
        """
        Adding Client Data into GET representation
        """
        data = super().to_representation(value)
        client = ClientSerializer(value.client)
        data['client'] = client.data
        return data
