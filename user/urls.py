from django.urls import path
from user import views

app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/update/', views.ManageUserView.as_view(), name='update-me'),
    path('me/', views.GetUserData.as_view(), name='me'),
]
