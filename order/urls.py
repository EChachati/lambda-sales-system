from django.urls import path, include
from rest_framework.routers import DefaultRouter

from order import views

router = DefaultRouter()

router.register('', views.OrderViewSet)
app_name = 'order'

urlpatterns = [
    path('order-sale',
         views.CreateProductOrderAPIView.as_view(), name='create-os'),
    path('', include(router.urls))
]
