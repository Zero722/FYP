from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.views.generic import ListView
from django.db.models import Q 
import json
import datetime

from .models import *
from .utils import cookieCart, cartData, guestOrder

# Create your views here.

def store(request):

    products = Product.objects.all()
    context = {'products':products}
    
    return render(request, 'store/store.html', context)

def details(request, product_id):

    try:
        productId = Product.objects.get(pk=product_id)
    except:
        raise Http404("Product doese not exist")


    context = {'product':productId}
    return render(request, 'store/details.html', context)
    
#Search
def get_products(request):
    search = request.GET.get('search')
    payload = []
    if search:
            # objs = Product.objects.filter(Q(name__icontains = search)|Q(name__startswith = search))
            # objs = Product.objects.filter(name__icontains = search)
            objs = Product.objects.filter(name__startswith = search)
            ob = Product.objects.filter(name__icontains = search)
        
            for obj in objs:
                payload.append({
                    'id' : obj.pk,
                    'imgurl' : obj.imageURL,
                    'name' : obj.name
                })

            for obj in ob:
                if obj not in objs:
                    payload.append({
                        'id' : obj.pk,
                        'imgurl' : obj.imageURL,
                        'name' : obj.name
                    })

    return JsonResponse({
        'status' : True,
        "payload" : payload
    })

def cart(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items':items, 'order':order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)
   

def checkout(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items':items, 'order':order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)
   
class SearchResultsView(ListView):
    model = Product
    template_name = 'store/search-product.html'
    context_object_name = 'products'

    def get_queryset(self):
        query = self.request.GET.get('search')
        product_starts = Product.objects.filter(name__startswith = query)
        product_contain = Product.objects.filter(Q(name__icontains = query), ~Q(name__startswith = query))
        products = {'starts':product_starts, 'contain':product_contain}
      
        return products
   
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('productId:', productId)
    print('Action:', action)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer = customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

# from django.views.decorators.csrf import csrf_exempt
# @csrf_exempt

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        
    else:
        customer, order = guestOrder(request, data)
    
    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()    

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment Complete', safe=False)
    