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



]