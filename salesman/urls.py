from django.urls import path, include
from rest_framework.routers import DefaultRouter

from salesman import views

router = DefaultRouter()
router.register('indicator', views.SalesmanIndicatorsViewSet,
                basename='indicator')
router.register('', views.SalesmanViewSet)

app_name = 'salesman'

urlpatterns = [
    path('', include(router.urls))
]
