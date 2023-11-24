from django.urls import path
from core import views
from core.serializers import LoginView

urlpatterns = [
    path('register/', views.RegistrationAPIView.as_view(), name=''),
    path('login/', LoginView.as_view(), name=''),
    path('email/', views.CheckEmailAPIView.as_view(), name=''),
]