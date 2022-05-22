from django.urls import path, include
from rest_framework.routers import DefaultRouter

from product import views

router = DefaultRouter()
router.register('category', views.CategoryViewSet)
router.register('barcode', views.BarcodeViewSet)
router.register('', views.ProductViewSet)

app_name = 'product'

urlpatterns = [
    path('ia', views.IAView.as_view(), name='ia'),
    path('', include(router.urls))
]
