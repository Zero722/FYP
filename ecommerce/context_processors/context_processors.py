import json
from store.models import *

def total_cart_items(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer, complete=False)
        cartItems = order.get_cart_items

    else:
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}

        items = []
        cartItems = 0

        for i in cart:
            try:
                cartItems += cart[i]["quantity"]
            
            except:
                pass

    return {'totalCartItems':cartItems}


