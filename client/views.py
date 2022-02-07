from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Client, ClientIndicator
from core.utils import upload_image
from client import serializers


class ClientViewSet(viewsets.ModelViewSet):
    """
    Manage Client in database
    """
    queryset = Client.objects.all()
    serializer_class = serializers.ClientSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        """
        Create a New Client
        """
        instance = super().create(request)
        client = Client.objects.get(pk=instance.data['id'])

        if client.image:
            client.image = upload_image(client.image)
        else:
            client.image = 'https://i.ibb.co/XF7qJN4/img-552555.png'

        instance.data['image'] = client.image.name
        client.save()
        obj = ClientIndicator.objects.create(client=client)
        obj.save()
        return instance


class ClientIndicatorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Get Client Indicators in Database
    """
    queryset = ClientIndicator.objects.all()
    serializer_class = serializers.ClientIndicatorSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
