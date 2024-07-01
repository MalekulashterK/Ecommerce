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

    path('place_order/', views.place_order),  
    path('my_order/', views.my_order),  
    path('my_order_details/<id>', views.my_order_details),  
    path('after_order/',views.after_order),

    path('categoryindex/',views.categoryindex),
    path('category_update/<id>',views.category_update),
    path('category_delete/<id>',views.category_delete),
    path('search_category/<id>',views.search_category),
    path('users/', views.users),
    path('order_report/', views.order_report),
    path('order_report_in/<id>', views.order_report_in),




    

]



urlpatterns += static('/cloud/', document_root='C:/cloud')

