from decimal import Decimal
from django.shortcuts import render, redirect,  get_object_or_404
from django.http import JsonResponse, Http404
from django.views.generic import ListView, View
from django.db.models import Q 
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm, CustomerForm, CheckoutForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import requests
import pandas as pd
from django.db.models import Case, When


import json
import datetime

from .models import *

# Create your views here.

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('store')
    else:
        return loginUser(request)


def loginUser(request):
    if 'next' in request.GET:
        messages.add_message(request, messages.INFO, 'Please log in, in order to perform the requested action.')
    page = 'login'
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('store')
        else:
            messages.add_message(request, messages.INFO, 'Invalid username or password')

    return render(request, 'store/login_register.html', {'page':page})


def logoutUser(request):
    logout(request)
    return redirect('login')


def registerUser(request):
    page = 'register'
    form = CustomUserCreationForm()
    customer_form = CustomerForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        customer_form = CustomerForm(request.POST)
        if form.is_valid() and customer_form.is_valid():
            user = form.save(commit=False)
            user.save()
            username = form.cleaned_data.get('username')
            customer_obj = Customer.objects.create(
                user = user,
                name = customer_form.cleaned_data.get('name'),
                email = customer_form.cleaned_data.get('email'),
                address = customer_form.cleaned_data.get('address'),
                contact = customer_form.cleaned_data.get('contact')
            )
            
            if user is not None:
                login(request, user)
                return redirect('store')

        else:
            messages.add_message(request, messages.INFO, 'Cannot register. Please fill valid information')


    context = {'form':form, 'page':page, 'customer_form': customer_form}
    return render(request, 'store/login_register.html', context)


def store(request):

    products = Product.objects.all()
    context = {'products':products}

    if request.user.is_authenticated:
        product_rating=pd.DataFrame(list(Myrating.objects.all().values()))
        print(product_rating)
        new_user=product_rating.user_id.unique().shape[0]
        current_user_id= request.user.id
        # if new user not rated any product
        if current_user_id>new_user:
            product=Product.objects.get(id=19)
            q=Myrating(user=request.user,product=product,rating=0)
            q.save()
        userRatings = product_rating.pivot_table(index=['user_id'],columns=['product_id'],values='rating')
        userRatings = userRatings.fillna(0,axis=1)
        corrMatrix = userRatings.corr(method='pearson')

        user = pd.DataFrame(list(Myrating.objects.filter(user=request.user).values())).drop(['user_id','id'],axis=1)
        user_filtered = [tuple(x) for x in user.values]
        product_id_watched = [each[0] for each in user_filtered]

        similar_products = pd.DataFrame()
        for product,rating in user_filtered:
            similar_products = similar_products.append(get_similar(product,rating,corrMatrix),ignore_index = True)

        products_id = list(similar_products.sum().sort_values(ascending=False).index)
        products_id_recommend = [each for each in products_id if each not in product_id_watched]
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(products_id_recommend)])
        product_list=list(Product.objects.filter(id__in = products_id_recommend).order_by(preserved)[:10])

        print('product=',product_list)
        context = {'product_list': product_list, 'products':products}    
        return render(request, 'store/store.html', context)

    context = {'products':products}
    return render(request, 'store/store.html', context)


def details(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
        
        if request.user.is_authenticated:
            user = get_object_or_404(Customer, user=request.user)
            temp = list(MyList.objects.all().values().filter(product_id=product_id,user=request.user))
            if temp:
                update = temp[0]['watch']
            else:
                update = False
            if request.method == "POST":

                # For my list
                if 'watch' in request.POST:
                    watch_flag = request.POST['watch']
                    if watch_flag == 'on':
                        update = True
                    else:
                        update = False
                    if MyList.objects.all().values().filter(product_id=product_id,user=request.user):
                        MyList.objects.all().values().filter(product_id=product_id,user=request.user).update(watch=update)
                    else:
                        q=MyList(user=request.user,product=product,watch=update)
                        q.save()
                    if update:
                        messages.success(request, "Product added to your list!")
                    else:
                        messages.success(request, "Product removed from your list!")

                    
                # For rating
                else:
                    rate = request.POST['rating']
                    if Myrating.objects.all().values().filter(product_id=product_id,user=request.user):
                        Myrating.objects.all().values().filter(product_id=product_id,user=request.user).update(rating=rate)
                    else:
                        q=Myrating(user=request.user,product=product,rating=rate)
                        q.save()

                    messages.success(request, "Rating has been submitted!")

                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            out = list(Myrating.objects.filter(user=request.user.id).values())

            # To display ratings in the product detail page
            product_rating = 0
            rate_flag = False
            for each in out:
                if each['product_id'] == product_id:
                    product_rating = each['rating']
                    rate_flag = True
                    break

            context = {'product': product,'product_rating':product_rating,'rate_flag':rate_flag,'update':update}
            return render(request, 'store/details.html', context)


    except:
        raise Http404("Product does not exist")

    context = {'product':product}
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


@login_required(login_url='login')
def cart(request):
    try:
        customer = get_object_or_404(Customer, user=request.user)
        order = Order.objects.get(customer=customer, ordered=False)
        context = {
            'object': order
        }
        return render(request, 'store/cart.html', context)

    except ObjectDoesNotExist:
        messages.warning(request, "You do not have an active order")
        return redirect("/")

   
class CheckoutView(LoginRequiredMixin, View):
    login_url = 'login'
    def get(self, *args, **kwargs):
        try:
            customer = get_object_or_404(Customer, user=self.request.user)
            order = Order.objects.get(customer=customer, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'order': order
            }
            return render(self.request, 'store/checkout.html', context)
        except ObjectDoesNotExist:
            return redirect('checkout')

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            customer = get_object_or_404(Customer, user=self.request.user)
            order = Order.objects.get(customer=customer, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                appartment_address = form.cleaned_data.get('appartment_address')
                country = form.cleaned_data.get('country')
                contact = form.cleaned_data.get('contact')
                shipping_address = ShippingAddress(
                    customer = get_object_or_404(Customer, user=self.request.user),
                    street_address = street_address,
                    apartment_address = appartment_address,
                    country = country,
                    contact = contact
                )
                shipping_address.save()
                order.shipping_address = shipping_address
                order.save()
                return redirect('payment')

        except ObjectDoesNotExist:
            return redirect("/")
        
        
class PaymentView(LoginRequiredMixin, View):
    login_url = 'login'
    def get(self, *args, **kwargs):
        try:
            customer = get_object_or_404(Customer, user=self.request.user)
            order = Order.objects.get(customer=customer, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'order': order
            }
            return render(self.request, 'store/payment.html', context)
        except ObjectDoesNotExist:
            return redirect('payment')
  
  
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
   
@login_required(login_url='login')
def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)
    customer = get_object_or_404(Customer, user=request.user)

    order_item, created = OrderItem.objects.get_or_create(
        product=product,
        customer=customer,
        ordered=False
    )
    order_qs = Order.objects.filter(customer=customer, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(product__id=product.id).exists():
            order_item.quantity += 1
            order_item.save()
            # messages.info(request, "This item quantity was updated.")            
            return redirect(request. META['HTTP_REFERER'])
        else:
            order.items.add(order_item)
            order_item.quantity += 1
            order_item.save()
            # messages.info(request, "This item was added to your cart.")            
            return redirect(request. META['HTTP_REFERER'])

    else:
        date_orderd = timezone.now()
        order = Order.objects.create(
            user=request.user, date_orderd=date_orderd)
        order.items.add(order_item)
        order_item.quantity += 1
        order_item.save()
        # messages.info(request, "This item was added to your cart.")        
        return redirect(request. META['HTTP_REFERER'])


@login_required(login_url='login')
def remove_from_cart(request, id):
    customer = get_object_or_404(Customer, user=request.user)
    product = get_object_or_404(Product, id=id)
    order_qs = Order.objects.filter(
        customer=customer,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(product__id=product.id).exists():
            order_item = OrderItem.objects.filter(
                product=product,
                customer=customer,
                ordered=False
            )[0]
            
            order_item.quantity -= 1
            order_item.save()

            if order_item.quantity <= 0:
                order.items.remove(order_item)
                order_item.delete()
            # messages.info(request, "This item quantity was updated.")
            return redirect(request. META['HTTP_REFERER'])
        else:
            # messages.info(request, "This item was not in your cart")
            return redirect(request. META['HTTP_REFERER'])
    else:
        # messages.info(request, "You do not have an active order")
        return redirect(request. META['HTTP_REFERER'])


@csrf_exempt
def verify_payment(request):
    customer = get_object_or_404(Customer, user=request.user)
    order = Order.objects.get(customer=customer, ordered=False)

    data = request.POST
    token = data['token']
    amount = data['amount']
    print("Amount: ",amount)
    print("Token: ",token)

    url = "https://khalti.com/api/v2/payment/verify/"
    payload = {
    "token": token,
    "amount": amount
    }
    headers = {
    "Authorization": "Key test_secret_key_319ae9296dd644e396434975266e231d"
    }

    response = requests.post(url, payload, headers = headers)

    response_data = json.loads(response.text)
    status_code = str(response.status_code)

    if status_code == '400':
        response = JsonResponse({'status':'false','message':response_data['detail']}, status=500)
        messages.error(request, 'Payment cannot be Processed.')

        return response

    # Creating Payment
    payment = Payment()
    payment.khalti_id = token
    payment.customer = customer
    payment.amount = float(amount)/100
    payment.save()

    # Assign payment to order
    order.ordered = True
    order.payment = payment
    order.save()
    messages.success(request, 'Payment Complete.')

    print("Amount: ",amount)
    print("Token: ",token)

    return JsonResponse(f"Payment Done !! With IDX. {response_data['user']['idx']}",safe=False)

@login_required(login_url='login')
def wishlist(request):
    products = Product.objects.filter(mylist__watch=True,mylist__user=request.user)
    query = request.GET.get('q')

    if query:
        products = Product.objects.filter(Q(title__icontains=query)).distinct()
        return render(request, 'store/watch.html', {'products': products})

    return render(request, 'store/wishlist.html', {'products': products})


# To get similar products based on user rating
def get_similar(product_name,rating,corrMatrix):
    similar_ratings = corrMatrix[product_name]*(rating-2.5)
    similar_ratings = similar_ratings.sort_values(ascending=False)
    return similar_ratings

