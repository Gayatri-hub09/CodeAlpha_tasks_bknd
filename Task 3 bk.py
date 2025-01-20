django-admin startproject restaurant_management_system
cd restaurant_management_system
python manage.py startapp restaurant

INSTALLED_APPS = [
    ...
    'restaurant',
]
from django.db import models

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name


class Reservation(models.Model):
    customer_name = models.CharField(max_length=100)
    number_of_people = models.IntegerField()
    date = models.DateTimeField()
    table_number = models.IntegerField()
    special_request = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Reservation for {self.customer_name} on {self.date}"


class InventoryItem(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.name


class Order(models.Model):
    order_date = models.DateTimeField(auto_now_add=True)
    customer_name = models.CharField(max_length=100)
    menu_items = models.ManyToManyField(MenuItem)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(choices=[('P', 'Pending'), ('C', 'Completed')], max_length=1, default='P')
    
    def calculate_total(self):
        self.total_amount = sum(item.price for item in self.menu_items.all())
        self.save()

    def __str__(self):
        return f"Order for {self.customer_name} on {self.order_date}"

    from django.contrib import admin
from .models import MenuItem, Reservation, InventoryItem, Order

admin.site.register(MenuItem)
admin.site.register(Reservation)
admin.site.register(InventoryItem)
admin.site.register(Order)

python manage.py makemigrations
python manage.py migrate

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Order, MenuItem, Reservation
from .forms import OrderForm, ReservationForm

def order_list(request):
    orders = Order.objects.all()
    return render(request, 'restaurant/order_list.html', {'orders': orders})

def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            order.calculate_total()
            return redirect('order_list')
    else:
        form = OrderForm()
    return render(request, 'restaurant/create_order.html', {'form': form})

def create_reservation(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('reservation_list')
    else:
        form = ReservationForm()
    return render(request, 'restaurant/create_reservation.html', {'form': form})

def menu_list(request):
    menu_items = MenuItem.objects.all()
    return render(request, 'restaurant/menu_list.html', {'menu_items': menu_items})

def reservation_list(request):
    reservations = Reservation.objects.all()
    return render(request, 'restaurant/reservation_list.html', {'reservations': reservations})

from django import forms
from .models import Order, Reservation

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'menu_items']

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['customer_name', 'number_of_people', 'date', 'table_number', 'special_request']
from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('order/create/', views.create_order, name='create_order'),
    path('reservation/create/', views.create_reservation, name='create_reservation'),
    path('menu/', views.menu_list, name='menu_list'),
    path('reservations/', views.reservation_list, name='reservation_list'),
]
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('restaurant.urls')),
]
<h1>Order List</h1>
<table>
    <tr>
        <th>Customer Name</th>
        <th>Total Amount</th>
        <th>Status</th>
    </tr>
    {% for order in orders %}
    <tr>
        <td>{{ order.customer_name }}</td>
        <td>{{ order.total_amount }}</td>
        <td>{{ order.get_status_display }}</td>
    </tr>
    {% endfor %}
</table>
<h1>Menu</h1>
<table>
    <tr>
        <th>Name</th>
        <th>Price</th>
        <th>Description</th>
    </tr>
    {% for item in menu_items %}
    <tr>
        <td>{{ item.name }}</td>
        <td>{{ item.price }}</td>
        <td>{{ item.description }}</td>
    </tr>
    {% endfor %}
</table>
<h1>Reservations</h1>
<table>
    <tr>
        <th>Customer Name</th>
        <th>Date</th>
        <th>Table Number</th>
    </tr>
    {% for reservation in reservations %}
    <tr>
        <td>{{ reservation.customer_name }}</td>
        <td>{{ reservation.date }}</td>
        <td>{{ reservation.table_number }}</td>
    </tr>
    {% endfor %}
</table>
python manage.py runserver
