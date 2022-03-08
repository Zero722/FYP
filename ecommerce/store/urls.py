from django.urls import path
from . import views
from .views import SearchResultsView

urlpatterns = [
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('product/<int:product_id>/', views.details, name='details'),
    path('search', SearchResultsView.as_view(), name='search_results'),
    path('get-products/',views.get_products, name='getproducts'),
    path('login/', views.loginUser, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerUser, name="register"),

    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),

]
