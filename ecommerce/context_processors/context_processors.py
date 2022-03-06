import json
from store.models import *

def total_cart_items(request):
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


