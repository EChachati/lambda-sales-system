from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from core.models import (
    Salesman,
    SalesmanIndicators,
    Client,
    ClientIndicator
)


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for UserModel
    """
    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name', 'identity_card', 'type')

        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8,
                'style': {'input_type': 'password'}
            }
        }

    def create(self, validated_data):
        """
        Create a new user with encrypted password.
        """
        if validated_data['type'] in ['SALESMAN', 'SALESMAN_AND_CLIENT']:
            validated_data['is_staff'] = True
            try:
                Salesman.objects.get(
                    identity_card=validated_data['identity_card'])
            except Salesman.DoesNotExist:
                salesman = Salesman.objects.create(
                    name=validated_data['name'],
                    identity_card=validated_data['identity_card'],
                    phone_1=validated_data['phone'],
                    address=validated_data['address']
                )
                indicators = SalesmanIndicators.objects.create(
                    salesman=salesman)
                salesman.save()
                indicators.save()

        if validated_data['type'] in ['CLIENT', 'SALESMAN_AND_CLIENT']:
            try:
                Client.objects.get(
                    identity_card=validated_data['identity_card']
                )
            except Client.DoesNotExist:
                client = Client.objects.create(
                    name=validated_data['name'],
                    identity_card=validated_data['identity_card'],
                    phone=validated_data['phone'],
                    address=validated_data['address']
                )
                indicators = ClientIndicator.objects.create(client=client)
                client.save()
                indicators.save()

        x = get_user_model().objects.create_user(**validated_data)
        return x

    def update(self, instance, validated_data):
        """
        actualice user, set password correctly and return user
        """
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    """
    Serializer for User Authentication
    """
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """
        Validate and authenticate users
        """
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
