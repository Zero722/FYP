from django.urls import path
from . import views
from .views import SearchResultsView, CheckoutView, PaymentView, verify_payment

urlpatterns = [
    path("", views.store, name="store"),
    path("cart/", views.cart, name="cart"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("payment", PaymentView.as_view(), name="payment"),
    path("search", SearchResultsView.as_view(), name="search_results"),
    path("product/<int:product_id>/", views.details, name="details"),
    path("get-products/", views.get_products, name="getproducts"),
    path("login/", views.custom_login, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("register/", views.registerUser, name="register"),
    path("add_to_cart/<int:id>/", views.add_to_cart, name="add_to_cart"),
    path("remove_from_cart/<int:id>/", views.remove_from_cart, name="remove_from_cart"),
    # payment url
    path("api/verify_payment", verify_payment, name="verify_payment"),
]
