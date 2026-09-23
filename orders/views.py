from django.shortcuts import render, redirect
from django.http import HttpResponse
from carts.models import CartItem
from .forms import OrderForm

# Create your views here.

def place_order(request, total=0, quantity=0):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # For now just create order logic will be added in next video
            # This is the initial version as per transcript
            pass
        return HttpResponse('Place order - form valid check')
    else:
        return redirect('checkout')
