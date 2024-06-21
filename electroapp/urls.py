from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.dashboard),
    path('user_login/', views.user_login),
    path('user_register/', views.user_register),
    path('user_logout/', views.user_logout),  
    path('dashboard/', views.dashboard),  
    path('dashboard1/', views.dashboard1),  
    path('admin_panel/', views.admin_panel),  

    path('productindex/',views.productindex),
    path('product_update/<id>',views.product_update),
    path('product_delete/<id>',views.product_delete),


]



urlpatterns += static('/cloud/', document_root='D:/cloud')

