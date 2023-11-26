from django.urls import path
from main import views

urlpatterns = [
    path('get_beneficiary/', views.GetUserBeneficiary.as_view(), name=''),
    path('create_beneficiary/', views.CreateUserBeneficiary.as_view(), name=''),
    path('del_beneficiary/', views.DeleteUserBeneficiary.as_view(), name=''),
    path('create_transaction_pin/', views.CreateTransactionPinAPIView.as_view(), name=''),
    path('update_transaction_pin/', views.UpdateTransactionPinAPIView.as_view(), name=''),
    path('get_exchange_rate/', views.GetExchangeRateAPIView.as_view(), name=''),
    path('get_exchange_rate_funding_account/', views.GetExchangeForFundingAccountAPIView.as_view(), name=''),
    path('fund_account/', views.FundAccountAPIView.as_view(), name=''),
    path('send_money/', views.SendMoneyAPIView.as_view(), name=''),
    path('user_dashboard/', views.UserDashBoardAPIView.as_view(), name=''),
    path('transaction_history/', views.TransactionHistoryAPIView.as_view(), name=''),
    path('debit_credit_history/', views.DebitCreditHistoryAPIView.as_view(), name=''),
    path('withdraw_money/', views.WithdrawalAPIView.as_view(), name=''),
    path('get_market_place/', views.GetP2PAPIView.as_view(), name=''),
    path('create_market_place/', views.CreateP2PAPIView.as_view(), name=''),
    path('delete_market_place/', views.DeleteP2PAPIView.as_view(), name=''),
]