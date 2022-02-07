from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Category, Product, Barcode
from core.utils import upload_image
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


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Manage category in database
    """
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class ProductViewSet(viewsets.ModelViewSet):
    """
    manage Products in Database
    """
    queryset = Product.objects.all()
    serializer_class = serializers.ProductSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        instance = super().create(request)
        product = Product.objects.get(pk=instance.data['id'])

        if product.image:
            product.image = upload_image(product.image)
        else:
            product.image = 'https://i.ibb.co/SrMrfyV/pngwing-com.png'

        instance.data['image'] = product.image.name
        product.save()
        return instance


class BarcodeViewSet(viewsets.ModelViewSet):
    """
    Manage Barcodes in Database
    """
    queryset = Barcode.objects.all()
    serializer_class = serializers.BarcodeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
