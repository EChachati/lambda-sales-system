from rest_framework import serializers
from core.models import Sale, ProductSale, Product

from product.serializers import ProductSerializer as OriginalProductSerializer
from product.serializers import CategorySerializer
from salesman.serializers import SalesmanSerializer
from client.serializers import ClientSerializer


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer used in sale for Product
    """

    class Meta:
        model = Product
        fields = '__all__'

    category = CategorySerializer()

    def serialize_sale_data(self, product_instance):
        """
        Method for serialize the Through model fields

        https://stackoverflow.com/questions/65493883/serialize-manytomanyfields-with-a-through-model-in-django-rest-framework
        """

        ProductSale_instance = product_instance\
            .productsale_set\
            .filter(
                sale=self.context['sale_instance']
            ).first()

        if ProductSale_instance:
            return ReducedProductSaleSerializer(ProductSale_instance).data
        return {}

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return {**rep, **self.serialize_sale_data(instance)}


class ReducedProductSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSale
        fields = ('quantity', 'income')


class ProductSaleSerializer(serializers.ModelSerializer):
    """
    Product-Sale Serializer
    """

    class ReducedSaleSerializer(serializers.ModelSerializer):
        salesman = SalesmanSerializer()
        client = ClientSerializer()

        class Meta:
            model = Sale
            fields = ('id', 'salesman', 'client',
                      'date', 'description')

    #product = OriginalProductSerializer()
    #sale = ReducedSaleSerializer()

    class Meta:
        model = ProductSale
        fields = ('product', 'sale', 'quantity', 'income')


class SaleSerializer(serializers.ModelSerializer):
    """
    Serializer for Sale
    """

    product = serializers.SerializerMethodField()

    def get_product(self, sale):

        return ProductSerializer(
            sale.product.all(),
            many=True,
            context={"sale_instance": sale}
        ).data

    class Meta:
        model = Sale
        fields = '__all__'
