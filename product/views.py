from rest_framework import viewsets, mixins, status
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import Category, Product, Barcode
from core.utils import upload_image, apply_query_filters, predict, load_model
from product import serializers, ia
from datetime import date


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

    def get_queryset(self):
        return apply_query_filters(self.request, self.queryset)


class ProductViewSet(viewsets.ModelViewSet):
    """
    manage Products in Database
    """
    queryset = Product.objects.all().order_by('name')
    serializer_class = serializers.ProductSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return apply_query_filters(self.request, self.queryset)

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

    def get_queryset(self):
        return apply_query_filters(self.request, self.queryset)


class IAView(APIView):
    permision_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request, *args, **kwargs):
        """
        > The function takes a request, and returns a prediction of the income or count of a product in  the next month

        :param request: the request object containing the product id and the
        :return: The predicted value for the next month.
        """

        model_type = 'income' if bool(request.data['income']) else 'count'
        var_type = 'product' if 'product_id' in request.data.keys() else 'category'

        model = load_model(f"{var_type}_{model_type}_per_month_model")

        if var_type == 'product':
            var_id = request.data['product_id']
            data = ia.get_grouped_product_data(to_dict=True)
            if not model:
                model = ia.train_model_product(
                    income=bool(request.data['income']))
        else:
            var_id = request.data['category_id']
            data = ia.get_grouped_category_data(to_dict=True)
            if not model:
                model = ia.train_model_category(
                    income=bool(request.data['income']))

        today = date.today()

        income, count = [], []
        try:
            income.append(data[var_id][today.year][2]['income'])
        except KeyError:
            income.append(0)
        try:
            count.append(data[var_id][today.year][2]['count'])
        except KeyError:
            count.append(0)

        ret = predict(model, income, count)  # count, income)

        return Response(ret, status=status.HTTP_200_OK)


"""
        first_year = list(data[product_id].keys())[1]
        first_year = first_year
        actual_year = date.today().year
        for year in range(first_year, actual_year + 1):
            for month in range(1, 13):
                if year == actual_year and month == 3:
                    break
                try:
                    income.append(data[product_id][year][month]['income'])
                except KeyError:
                    income.append(0)
                try:
                    count.append(data[product_id][year][month]['count'])
                except KeyError:
                    count.append(0)
"""
