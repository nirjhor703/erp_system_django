from django.urls import path
from pharmacy.views.setup.manufacturers import *
from pharmacy.views.setup.categories import *
from pharmacy.views.setup.units import *
from pharmacy.views.setup.forms import *
from pharmacy.views.setup.transaction_groupes import *
from pharmacy.views.transaction import pharmacypurchase
from pharmacy.views.setup.pharmacy_products import *



# urlpatterns = [
#     path('medicine/add/', views.add_medicine, name='add-medicine'),
#     path('medicine/list/', views.medicine_list, name='medicine-list'),
#     path('medicine/search/', views.medicine_search, name='medicine-search'),  # AJAX search
#     path('medicine/save/', views.save_medicine, name='save-medicine'),        # AJAX save
# ]

urlpatterns = [
    # path('medicine/add/', pharmacypurchase.medicine_add, name='medicine-add'),
    path('medicine/', pharmacypurchase.medicine_list, name='medicine-list'),

    path('product-search/', pharmacypurchase.product_search, name='product-search'),

    # path('get-products/', views.get_products, name='get-products'),
    path('get-stores/', pharmacypurchase.get_stores, name='get_stores'),
    path('get-suppliers/', pharmacypurchase.get_suppliers, name='get_suppliers'),
    path('get-divisions/', pharmacypurchase.get_divisions, name='get_divisions'),
    path('ajax/get-groups/', get_groups_by_type, name='get_groups_by_type'),

    
    
    # path('transaction/get/<str:tran_id>/', pharmacypurchase.get_transaction, name='get_transaction'),


    # path('verify-transaction/<str:tran_id>/', views.get_transaction_for_verify, name='verify_transaction_detail'),
    # path('verify-transaction/', views.verify_transaction, name='verify_transaction'),  # POST
    # urls.py
    # urls.py
    # path("transaction/<str:tran_id>/details/", views.get_transaction_details, name="get_transaction_details"),

    # path("transaction/temp/update/<str:tran_id>/", views.update_transaction_temp, name="update_transaction_temp"),
    # path("transaction/get/<str:tran_id>/", pharmacypurchase.get_transaction, name="get_transaction"),


    # path("transaction/temp/details/<str:tran_id>/", views.get_temp_details),




    
    path('transaction/temp/create/', pharmacypurchase.create_transaction_temp, name='create_transaction_temp'),
    path("transaction-temp/verify/", pharmacypurchase.verify_transaction, name="verify_transaction"),
    path("transaction-main/get/", pharmacypurchase.get_transaction_main, name="get_transaction_main"),
    path("transaction/edit-data/<str:tran_id>/",pharmacypurchase.get_transaction_for_edit,name="transaction_edit_data"
    ),
    # path('transaction-details-temp/delete/<int:temp_id>/', pharmacypurchase.delete_unverified_transaction, name='delete_unverified_transaction'),
    # path('transaction-main/delete/<int:main_id>/', pharmacypurchase.delete_verified_transaction, name='delete_verified_transaction'),

    path("transaction/delete/<str:tran_id>/", pharmacypurchase.delete_transaction, name="delete_transaction"),



    path('manufacturer/', manufacturer_list, name='manufacturer_list'),
    path('add_manufacturer/', add_manufacturer, name='add_manufacturer'),
    path('get_manufacturer/<int:id>/', get_manufacturer, name='get_manufacturer'),
    path('update_manufacturer/', update_manufacturer, name='update_manufacturer'),
    path('delete_manufacturer/<int:id>/', delete_manufacturer, name='delete_manufacturer'),
    
    
    path('category/', category_list, name='category_list'),
    path('add_category/', add_category, name='add_category'),
    path('get_category/<int:id>/',get_category, name='get_category'),
    path('update_category/',update_category, name='update_category'),
    path('delete_category/<int:id>/',delete_category, name='delete_category'),
    path('ajax/get-groups/', get_groups_by_type, name='get_groups_by_type'),
    
    
    path('item_units/', unit_list, name='unit_list'),
    path('add_unit/', add_unit, name='add_unit'),
    path('get_unit/<int:id>/', get_unit, name='get_unit'),
    path('update_unit/', update_unit, name='update_unit'),
    path('delete_unit/<int:id>/', delete_unit, name='delete_unit'),
    
    
    path('item_forms/', form_list, name='form_list'),
    path('add_form/', add_form, name='add_form'),
    path('get_form/<int:id>/', get_form, name='get_form'),
    path('update_form/', update_form, name='update_form'),
    path('delete_form/<int:id>/', delete_form, name='delete_form'),

    path('transaction-groupes/', transaction_groupe_list, name='transaction_groupe_list'),
    path('transaction-groupes/add/', add_transaction_groupe, name='add_transaction_groupe'),
    path('transaction-groupes/get/', get_transaction_groupe, name='get_transaction_groupe'),
    path('transaction-groupes/update/', update_transaction_groupe, name='update_transaction_groupe'),
    path('transaction-groupes/delete/', delete_transaction_groupe, name='delete_transaction_groupe'),


    path('pharmacy-products/', pharmacy_products_list, name='pharmacy_products_list'),
    path('pharmacy-products/add/', pharmacy_product_add, name='pharmacy_product_add'),
    path('pharmacy-products/edit/<int:id>/', pharmacy_product_edit, name='pharmacy_product_edit'),
    path('pharmacy-products/delete/<int:id>/', pharmacy_product_delete, name='pharmacy_product_delete'),


]




