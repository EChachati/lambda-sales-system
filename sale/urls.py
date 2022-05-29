from django.urls import path, include
from rest_framework.routers import DefaultRouter

from sale import views

router = DefaultRouter()

router.register('', views.SaleViewSet)
app_name = 'sale'

urlpatterns = [
    path('product-sale',
         views.CreateProductSaleAPIView.as_view(), name='create-ps'),
    path('salesman/<int:pk>', views.GetSalesBySaleman.as_view(),
         name='get-sales-by-saleman'),
    path('ia', views.IAView.as_view(), name='ia'),
    path('statistic', views.StatisticView.as_view(), name='statistic'),
    path('biggest-sale', views.GetBiggestSale.as_view(), name='biggest-sale'),
    path('update-ps', views.UpdateProductSale.as_view(), name='update-ps'),
    path('', include(router.urls))
]
