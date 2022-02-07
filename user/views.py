from user.serializers import UserSerializer, AuthTokenSerializer
from rest_framework import generics, authtoken, permissions, authentication
from rest_framework.authtoken.views import ObtainAuthToken

from rest_framework.settings import api_settings


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


class ManageUserView(generics.RetrieveUpdateAPIView):
    """
    Manage Auth User
    """
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """
        get Authenticated user
        """
        return self.request.user
