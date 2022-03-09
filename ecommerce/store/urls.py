from django.urls import path
from . import views
from .views import SearchResultsView

urlpatterns = [
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    # path('checkout/', views.checkout, name="checkout"),
    path('product/<int:product_id>/', views.details, name='details'),
    # path('cart/', OrderSummaryView.as_view(), name='cart'),
    path('search', SearchResultsView.as_view(), name='search_results'),
    path('get-products/',views.get_products, name='getproducts'),
    path('login/', views.custom_login, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerUser, name="register"),

    # path('update_item/', views.updateItem, name="update_item"),
    # path('process_order/', views.processOrder, name="process_order"),
    path('add_to_cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:id>/', views.remove_from_cart, name='remove_from_cart'),



]
