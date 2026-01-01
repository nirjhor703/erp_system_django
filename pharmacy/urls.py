from django.urls import path
from pharmacy import views

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

    # path('get-products/', views.get_products, name='get-products'),
    path('get-stores/', views.get_stores, name='get_stores'),
    path('get-suppliers/', views.get_suppliers, name='get_suppliers'),
    path('get-divisions/', views.get_divisions, name='get_divisions'),
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





]