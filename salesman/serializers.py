from rest_framework import serializers

from core.models import Salesman, SalesmanIndicators


class SalesmanSerializer(serializers.ModelSerializer):
    """
    Serializer for Salesman Object
    """
    class Meta:
        model = Salesman
        fields = '__all__'

    def to_representation(self, instance):
        """
        Override to_representation to add image field
        """
        representation = super().to_representation(instance)
        representation['image'] = instance.image.name
        return representation


class SalesmanIndicatorsSerializer(serializers.ModelSerializer):
    """
    Serializer for special Salesman data
    """

    class Meta:
        model = SalesmanIndicators
        fields = '__all__'
        read_only_fields = (
            'salesman',
            'purchases',
            'money_generated',
            'biggest_sale'
        )

    def to_representation(self, value):
        """
        Adding Salesman data into GET representation
        """
        data = super().to_representation(value)
        salesman_serializer = SalesmanSerializer(value.salesman)
        data['salesman'] = salesman_serializer.data
        return data
