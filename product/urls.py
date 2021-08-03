from django.urls import path, include
from rest_framework.routers import DefaultRouter

from product import views

router = DefaultRouter()
router.register('category', views.CategoryViewSet)
router.register('', views.ProductViewSet)
router.register('barcode', views.BarcodeViewSet)

app_name = 'product'

urlpatterns = [
    path('', include(router.urls))
]
