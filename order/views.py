from rest_framework import viewsets, status
from rest_framework.generics import ListCreateAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Order, ProductOrder
from order import serializers


class OrderViewSet(viewsets.ModelViewSet):
    """
    Manage Orders in Database
    """
    queryset = Order.objects.all().order_by('-date', '-id')
    serializer_class = serializers.OrderSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        It takes a request object and a queryset, and returns a queryset that has been filtered
        according to the query parameters in the request
        :return: The queryset is being returned.
        """
        return apply_query_filters(self.request, self.queryset)


class CreateProductOrderAPIView(ListCreateAPIView):
    """
    Create multiple products with one Post using a list
    """
    queryset = ProductOrder.objects.all()
    serializer_class = serializers.ProductOrderSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        """
        It creates a ProductOrder object for each item in the request.data list

        :param request: The request object
        :return: A list of ProductOrder objects
        """
        serializer = self.get_serializer(
            data=request.data, many=isinstance(request.data, list))
        ps_created = []
        for data in request.data:
            if not (
                'product' in data.keys() and data['product']
                and 'sale' in data.keys() and data['sale']
                    and 'income' in data.keys() and data['income']):
                return Response(request.data, status=status.HTTP_400_BAD_REQUEST)

            data['product'] = Product.objects.get(pk=data['product'])
            data['sale'] = Sale.objects.get(pk=data['sale'])
            ps_obj = ProductOrder.objects.create(**data)
            ps_created.append(ps_obj.id)

        results = ProductOrder.objects.filter(id__in=ps_created)
        output_serializer = serializers.ProductOrderSerializer(
            results, many=True)
        data = output_serializer.data[:]
        return Response(data, status=status.HTTP_201_CREATED)
