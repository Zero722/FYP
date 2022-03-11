from sqlite3 import Timestamp
from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import SET_NULL
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(max_length=200, null=True)
    address = models.CharField(max_length=200, null=True) #added
    contact = models.BigIntegerField(null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    digital = models.BooleanField(default=False, null=True, blank=False)
    image = models.ImageField(null=True, blank=True)
    status = models.BooleanField(default=False, null=True, blank=False) #changed
    description = models.TextField(max_length=1000, null=True, blank=True) #added

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

class OrderItem(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    ordered = models.BooleanField(default=False)

    @property
    def get_total_item_price(self):
        total = self.product.price * self.quantity
        return total

    def __str__(self):
        info = str(self.quantity)+" of "+str(self.product.name)
        return str(info)

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    date_orderd = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False, null=False, blank=False)
    being_delivered = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=200, null=True)
    total_price = models.FloatField(max_length=200, null=True) #added
    sphipping_address = models.ForeignKey('ShippingAddress', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)



    def __str__(self):
            return str(self.customer.user)

    def get_total(self):
        total = 0
        for order_items in self.items.all():
            total = total + order_items.get_total_item_price
        return total


    @property
    def get_cart_items(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.quantity
        return total


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    street_address = models.CharField(max_length=200, null=True)
    apartment_address = models.CharField(max_length=200, null=True)
    country = models.CharField(max_length=200, null=True)
    contact = models.BigIntegerField(null=True)

    def __str__(self):
        return str(self.customer.user)


class Payment(models.Model):
    khalti_id = models.CharField(max_length=100)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.customer.user)

class Myrating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0, validators=[MaxValueValidator(5), MinValueValidator(0)])

class MyList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    watch = models.BooleanField(default=False)




    

