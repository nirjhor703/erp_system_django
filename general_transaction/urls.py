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
    path('get-transaction-with-combo-p/', views.get_transaction_with_combo_p,name="get_transaction_with_combo_p"),
    path('payment/save-payment/', views.save_general_payment, name='save_payment'),


    path('receive/add/', views.add_receive_page, name='add_receive_page'),
    path('receive/', views.receive_list, name='receive_list'),
    path('receive/save-receive/', views.save_general_receive, name='save_general_receive'),
    path('receive/load/', views.receive_list_load, name='receive_list_load'),
    path('receive/report/pdf/', views.receive_report_pdf, name='receive_report_pdf'),
    path('get-transaction-with-combo-r/', views.get_transaction_with_combo_r,name="get_transaction_with_combo_r"),
    path('get-supplier-by-tran-with-g/', views.get_supplier_by_tran_with_g, name='get_supplier_by_tran_with_g'),
     path('get-supplier-combo-g/', views.get_supplier_combo_g, name='get_supplier_combo_g'),
]