from django.urls import path
from . import views

urlpatterns = [
    path('heads', views.transaction_heads, name='transaction_heads'),
    path('tranhead_add/', views.transaction_head_add, name='transaction_head_add'),
    path('tranhead_edit/<int:id>/', views.transaction_head_edit, name='transaction_head_edit'),
    path('tranhead_delete/<int:id>/', views.transaction_head_delete, name='transaction_head_delete'),
]
