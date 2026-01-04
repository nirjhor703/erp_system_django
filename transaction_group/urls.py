from django.urls import path
from . import views

urlpatterns = [
    path('transaction-groupes/', views.transaction_groupe_page, name='transaction_groupe_page'),
    path('transaction-groupe/store/', views.transaction_groupe_store),
    path('transaction-groupe/fetch/', views.transaction_groupe_fetch),
    path('transaction-groupe/update/', views.transaction_groupe_update),
    path('transaction-groupe/delete/', views.transaction_groupe_delete),

]