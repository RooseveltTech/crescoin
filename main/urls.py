from django.urls import path
from main import views

urlpatterns = [
    path('get_beneficiary/', views.GetUserBeneficiary.as_view(), name=''),
    path('create_beneficiary/', views.CreateUserBeneficiary.as_view(), name=''),
    path('del_beneficiary/', views.DeleteUserBeneficiary.as_view(), name=''),
    path('create_transaction_pin/', views.CreateTransactionPinAPIView.as_view(), name=''),
    path('update_transaction_pin/', views.UpdateTransactionPinAPIView.as_view(), name=''),
]