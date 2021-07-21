from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Category
from product import serializers


class BaseViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    """
    Base Atributes for ViewSets
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Return objects for Autheticated User
        """
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """
        Create new object
        """
        serializer.save(user=self.request.user)


class CategoryViewSet(BaseViewSet):
    """
    Manage category in database
    """
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
