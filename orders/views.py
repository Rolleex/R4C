from django.http import JsonResponse
from django.shortcuts import render
from .forms import OrderForm
from robots.models import Robot
from customers.forms import CustomerForm


# Create your views here.
def place_order(request):
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        customer_form = CustomerForm(request.POST)
        if order_form.is_valid() and customer_form.is_valid():
            new_customer = customer_form.save(commit=False)
            new_customer.save()
            new_order = order_form.save(commit=False)
            new_order.customer = new_customer
            new_order.save()
            if Robot.objects.filter(serial=order_form['robot_serial']).exists():
                return JsonResponse({'message': 'Спасибо за заказ!'}, status=201)
            else:
                return JsonResponse({'message': 'Робота нет в наличии'})
        else:
            return JsonResponse({'message': 'Данные не прошли валидацию'}, status=400)
    else:
        customer_form = CustomerForm()
        order_form = OrderForm()
    return render(request, 'orders/make_order.html', {'form': order_form, 'form2': customer_form})
