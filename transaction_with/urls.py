from django.urls import path
from . import views

urlpatterns = [
    path('transaction-withs/', views.transaction_with_page, name='transaction_with_page'),
    path('transaction-with/store/', views.transaction_with_store),
    path('transaction-with/fetch/', views.transaction_with_fetch),
    path('transaction-with/update/', views.transaction_with_update),
    path('transaction-with/delete/', views.transaction_with_delete),
]