from django.urls import path
from general_transaction import views
from . import views

urlpatterns = [
# PAGE
    path('payment/add-payment/', views.add_payment_page, name='add_payment_page'),
    path('payment/', views.payment_list, name='payment_list'),
    path('product-search/', views.product_search, name='general-product-search'),
    path('payment/load/', views.payment_list_load, name='payment_list_load'),
    path('payment/report/pdf/', views.payment_report_pdf, name='payment_report_pdf'),
    path('get-transaction-with-users-combo/', views.get_transaction_with_users_combo,name="get_transaction_with_users_combo"),
    path('payment/save-payment/', views.save_general_payment, name='save_payment'),
]