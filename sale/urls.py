from django.urls import path, include
from rest_framework.routers import DefaultRouter

from sale import views

router = DefaultRouter()
router.register('product-sale', views.PSViewSet)
router.register('', views.SaleViewSet)
app_name = 'sale'

urlpatterns = [
    path('', include(router.urls))
]
