from rest_framework import serializers
from core.models import Sale, ProductSale, Product


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer used in sale for Product
    """
    class Meta:
        model = Product
        fields = '__all__'

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
            return ProductSaleSerializer(ProductSale_instance).data
        return {}

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return {**rep, **self.serialize_sale_data(instance)}


class ProductSaleSerializer(serializers.ModelSerializer):
    """
    Product-Sale Serializer
    """
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

    def create(self, validated_data):
        import pdb
        pdb.set_trace()

        products_data = validated_data.pop('products')
        sale = Sale.objects.create(**validated_data)
        for product_data in products_data:
            ProductSale.objects.create(**validated_data)

        return sale
