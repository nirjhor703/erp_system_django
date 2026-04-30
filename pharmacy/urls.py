from django.urls import path
from pharmacy import views
from . import views

# urlpatterns = [
#     path('medicine/add/', views.add_medicine, name='add-medicine'),
#     path('medicine/list/', views.medicine_list, name='medicine-list'),
#     path('medicine/search/', views.medicine_search, name='medicine-search'),  # AJAX search
#     path('medicine/save/', views.save_medicine, name='save-medicine'),        # AJAX save
# ]

urlpatterns = [
    path('medicine/add/', views.medicine_add, name='medicine-add'),
    path('medicine/', views.medicine_list, name='medicine-list'),

    path('product-search/', views.product_search, name='product-search'),
    path('purchase-list/', views.purchase_list, name='purchase-list'),    
    path('purchase-list-load/', views.purchase_list_load, name='purchase-list-load'),
    path('pharmacy/add-purchase/', views.add_purchase_page, name='add_purchase_page'),
    path('pharmacy/save-purchase/', views.save_purchase, name='save_purchase'),    

    path('issue-list/', views.issue_list, name='issue-list'),
    path('pharmacy/add-issue/', views.add_issue_page, name='add_issue_page'),
    path('pharmacy/save-issue/', views.save_issue, name='save_issue'),
    path("pharmacy/issue-invoice/<str:tran_id>/", views.issue_invoice, name="issue_invoice"),
    path(
    "pharmacy/download-issue-pdf/<str:tran_id>/",
    views.download_issue_pdf,
    name="download_issue_pdf"
    ),
    
    path('pharmacy/add-order/', views.add_order_page, name='add_order_page'),
    path('pharmacy/save-order/', views.save_order, name='save_order'),
    path('order-list/', views.order_list, name='order_list'),
    path("search-po/", views.search_po, name="search_po"),
    path("get-po-details/", views.get_po_details, name="get_po_details"),

    # path('get-products/', views.get_products, name='get-products'),
    path('get-stores/', views.get_stores, name='get_stores'),
    path('get-suppliers/', views.get_suppliers, name='get_suppliers'),
    path('get-divisions/', views.get_divisions, name='get_divisions'),
    path('get-divisions-combo/', views.get_divisions_combo, name='get_divisions_combo'),
    path('get-supplier-combo/', views.get_supplier_combo, name='get_supplier_combo'),
    path('get-bank-combo/', views.get_bank_combo, name='get_bank_combo'),
    path('get-store-combo/', views.get_store_combo, name='get_store_combo'),
    path('get-transaction-with/', views.get_transaction_with_combo, name='get_transaction_with_combo'),
    path('get-transaction-with-issue/', views.get_transaction_with_combo_issue, name='get_transaction_with_combo_issue'),
    path('get-supplier-by-tran-with/', views.get_supplier_by_tran_with, name='get_supplier_by_tran_with'),
    path('transaction/get/<str:tran_id>/', views.get_transaction, name='get_transaction'),



    # path('verify-transaction/<str:tran_id>/', views.get_transaction_for_verify, name='verify_transaction_detail'),
    # path('verify-transaction/', views.verify_transaction, name='verify_transaction'),  # POST
    # urls.py
    # urls.py
    # path("transaction/<str:tran_id>/details/", views.get_transaction_details, name="get_transaction_details"),

    # path("transaction/temp/update/<str:tran_id>/", views.update_transaction_temp, name="update_transaction_temp"),
    path("transaction/get/<str:tran_id>/", views.get_transaction, name="get_transaction"),


    # path("transaction/temp/details/<str:tran_id>/", views.get_temp_details),

    
    path('transaction/temp/create/', views.create_transaction_temp, name='create_transaction_temp'),
    # path('transaction/temp/test-tran-id/', views.test_tran_id_generation),
    # path('transaction/temp/create/', views.create_transaction_temp),
    # urls.py
    # urls.py
    # path('transaction/<str:tran_id>/edit-data/', views.get_transaction_for_edit, name='get_transaction_for_edit'),


    path('purchase/report/pdf/', views.purchase_report_pdf, name='purchase_report_pdf'),

]