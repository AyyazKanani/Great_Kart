from django.shortcuts import render, redirect
from django.http import HttpResponse
from carts.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import datetime

# Create your views here.

def place_order(request, total=0, quantity=0):
    # Not logged in -> no 500 error, just send to login page
    if not request.user.is_authenticated:
        return redirect('login')

    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            for item in cart_items:
                total += (item.product.price * item.quantity)
                quantity += item.quantity
            tax = (2 * total)/100
            grand_total = total + tax

            data.order_total = grand_total
            data.tax = tax
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)
        else:
            return redirect('checkout')
    else:
        return redirect('checkout')


def payments(request):
    # Demo payment - no PayPal needed
    # This runs when user clicks "Pay Now (Demo)" on payments.html
    if request.method == 'POST':
        order_number = request.POST.get('order_number')
        order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)

        # 1. Create dummy Payment
        payment = Payment(
            user=request.user,
            payment_id=order_number,  # demo id = order number
            payment_method='Demo',
            amount_paid=order.order_total,
            status='Completed',
        )
        payment.save()

        # 2. Link payment to order and mark ordered
        order.payment = payment
        order.is_ordered = True
        order.save()

        # 3. Move cart items to OrderProduct table
        cart_items = CartItem.objects.filter(user=request.user)
        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order = order
            orderproduct.payment = payment
            orderproduct.user = request.user
            orderproduct.product = item.product
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()

            # copy variations (color, size)
            variations = item.variations.all()
            orderproduct.variation.set(variations)
            orderproduct.save()

            # 4. Reduce stock
            product = Product.objects.get(id=item.product.id)
            product.stock -= item.quantity
            product.save()

        # 5. Clear cart
        CartItem.objects.filter(user=request.user).delete()

        # 6. Send order email (prints in terminal, console backend)
        mail_subject = 'Thank you for your order!'
        message = render_to_string('orders/order_recieved_email.html', {
            'user': request.user,
            'order': order,
        })
        to_email = request.user.email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()

        # 7. Go to success page
        return redirect('/orders/order_complete/?order_number=' + order.order_number + '&payment_id=' + payment.payment_id)

    return redirect('store')


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        payment = Payment.objects.get(payment_id=transID)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
