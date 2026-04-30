from django.urls import path
from bank_transaction import views
from . import views

urlpatterns = [
# PAGE
    path('deposit/add-deposit/', views.add_deposit_page, name='add_deposit_page'),
    path('deposit/', views.deposit_list, name='deposit_list'),
    path('product-search/', views.product_search, name='bank-product-search'),
    path('deposit/load/', views.deposit_list_load, name='deposit_list_load'),
    path('deposit/report/pdf/', views.deposit_report_pdf, name='deposit_report_pdf'),
    path('get-transaction-with-users-combo/', views.get_transaction_with_users_combo,name="get_transaction_with_users_combo"),
    path('deposit/save-deposit/', views.save_bank_deposit, name='save_bank_deposit'),
]