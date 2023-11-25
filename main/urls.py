from django.urls import path
from main import views

urlpatterns = [
    path('get_beneficiary/', views.GetUserBeneficiary.as_view(), name=''),
    path('create_beneficiary/', views.CreateUserBeneficiary.as_view(), name=''),
    path('del_beneficiary/', views.DeleteUserBeneficiary.as_view(), name=''),
]