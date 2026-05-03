from django.urls import path
from bank_transaction import views

urlpatterns = [
    # =========================
    # DEPOSIT
    # =========================
    path('deposit/add-deposit/', views.add_deposit_page, name='add_deposit_page'),
    path('deposit/', views.deposit_list, name='deposit_list'),
    path('deposit/load/', views.deposit_list_load, name='deposit_list_load'),
    path('deposit/report/pdf/', views.deposit_report_pdf, name='deposit_report_pdf'),
    path('deposit/save-deposit/', views.save_bank_deposit, name='save_bank_deposit'),

    # =========================
    # WITHDRAW
    # =========================
    path('withdraw/add-withdraw/', views.add_withdraw_page, name='add_withdraw_page'),
    path('withdraw/', views.withdraw_list, name='withdraw_list'),
    path('withdraw/load/', views.withdraw_list_load, name='withdraw_list_load'),
    path('withdraw/report/pdf/', views.withdraw_report_pdf, name='withdraw_report_pdf'),
    path('withdraw/save-withdraw/', views.save_bank_withdraw, name='save_bank_withdraw'),

    # =========================
    # COMMON
    # =========================
    path('product-search/', views.product_search, name='bank_product_search'),
    path(
        'get-transaction-with-users-combo/',
        views.get_transaction_with_users_combo,
        name='get_transaction_with_users_combo'
    ),
]