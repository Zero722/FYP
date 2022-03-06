from django.urls import path
from . import views

urlpatterns = [
    path('get-products/',views.get_products, name='getproducts'),
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('product/<int:product_id>/', views.details, name='details'),

    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),

]
