from user.serializers import UserSerializer, AuthTokenSerializer
from rest_framework import generics, authtoken, permissions, authentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from core.models import Salesman, Client, SalesmanIndicators, ClientIndicator


class CreateUserView(generics.CreateAPIView):
    """
    Create a new User in system
    """
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """
    Create new Authenticated token for user
    """
    serializer_class = AuthTokenSerializer
    #renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.UpdateAPIView):
    """
    Manage Auth User
    """
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)


class GetUserData(APIView):
    """
    Get Authenticated user data
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        """
        Return Authenticated user data
        """
        user = self.request.user
        data = user.to_dict()

        if user.type in ['SALESMAN', 'SALESMAN_AND_CLIENT']:
            salesman = Salesman.objects.get(identity_card=user.identity_card)

            #data['salesman'] = salesman.to_dict()
            data['salesman'] = SalesmanIndicators.objects.get(
                salesman=salesman).to_dict()

        if user.type in ['CLIENT', 'SALESMAN_AND_CLIENT']:
            client = Client.objects.get(identity_card=user.identity_card)

            #data['client'] = client.to_dict()
            data['client'] = ClientIndicator.objects.get(
                client=client).to_dict()

        return Response(data)
