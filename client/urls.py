from django.urls import path, include
from rest_framework.routers import DefaultRouter

from client import views

router = DefaultRouter()
router.register(
    'indicator',
    views.ClientIndicatorViewSet,
    basename='indicator'
)
router.register('', views.ClientViewSet)

app_name = 'client'

urlpatterns = [
    path('ia', views.IAView.as_view(), name='ia'),
    path('statistic', views.StatisticsView.as_view(), name='statistic'),
    path('', include(router.urls))
]
