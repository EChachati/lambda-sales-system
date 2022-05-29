from rest_framework import serializers
from core.models import Order, ProductOrder, Product, Sale
from product.serializers import ProductSerializer as OriginalProductSerializer
from salesman.serializers import SalesmanSerializer
from client.serializers import ClientSerializer
from product.serializers import CategorySerializer


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer used in sale for Product
    """

    class Meta:
        model = Product
        fields = '__all__'

    category = CategorySerializer()

    def serialize_order_data(self, product_instance):
        """
        Method for serialize the Through model fields

        https://stackoverflow.com/questions/65493883/serialize-manytomanyfields-with-a-through-model-in-django-rest-framework
        """

        ProductOrder_instance = product_instance\
            .productorder_set\
            .filter(
                order=self.context['order_instance']
            ).first()

        if ProductOrder_instance:
            return ReducedProductOrderSerializer(ProductOrder_instance).data
        return {}

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return {**rep, **self.serialize_sale_data(instance)}


class ReducedProductOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOrder
        fields = ('quantity', 'income')


class ProductOrderSerializer(serializers.ModelSerializer):
    """
    Product Order Serializer
    """

    class Meta:
        model = ProductOrder
        fields = ('product', 'order', 'quantity', 'income')

    def to_representation(self, value):
        """
        """
        data = super().to_representation(value)
        product = OriginalProductSerializer(value.product)
        data['product'] = product.data
        return data


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Order
    """

    product = serializers.SerializerMethodField()

    def get_product(self, order):

        return ProductSerializer(
            order.product.all(),
            many=True,
            context={"order_instance": order}
        ).data

    class Meta:
        model = Order
        fields = '__all__'

    def to_representation(self, value):
        """
        Adding Salesman and Client representation
        """
        data = super().to_representation(value)
        salesman = SalesmanSerializer(value.salesman)
        client = ClientSerializer(value.client)
        data['salesman'] = salesman.data
        data['client'] = client.data
        return data
