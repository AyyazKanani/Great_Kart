from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating, ProductGallery, Variation
from .forms import ReviewForm
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.db.models import Q
from django.contrib import messages
from orders.models import OrderProduct

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse

# Create your views here.

def store(request, category_slug=None):
    categories = None
    products = None

    # Sidebar filters (Size + Price) - from URL like ?size=M&min_price=100&max_price=500
    selected_size = request.GET.get('size', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 1)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')

        # Apply size filter (products having this size variation)
        if selected_size:
            products = products.filter(
                variation__variation_category='size',
                variation__variation_value__iexact=selected_size,
                variation__is_active=True,
            ).distinct()

        # Apply price filter (ignore wrong values safely)
        try:
            if min_price != '':
                products = products.filter(price__gte=int(min_price))
        except ValueError:
            min_price = ''
        try:
            if max_price != '':
                products = products.filter(price__lte=int(max_price))
        except ValueError:
            max_price = ''

        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()  # python counting method = count()

    # Sizes available in shop (for sidebar buttons)
    all_sizes = Variation.objects.filter(
        variation_category='size', is_active=True, product__is_available=True,
    ).values_list('variation_value', flat=True).distinct()

    # Keep filters in pagination links (page number removed, rest kept)
    params = request.GET.copy()
    params.pop('page', None)
    filter_query = params.urlencode()

    context = {
        'products': paged_products,
        'product_count': product_count,
        'all_sizes': sorted(set(all_sizes)),
        'selected_size': selected_size,
        'min_price': min_price,
        'max_price': max_price,
        'filter_query': filter_query,
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)  # __(underscore,underscore is a syntax to get the data from models)_
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists() # __(underscore, underscore)we are going to check cart model here
    except Exception as e:
            raise e

    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    # Get the product gallery
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    context = {
        'single_product' : single_product,
        'in_cart'        : in_cart,
        'orderproduct'   : orderproduct,
        'reviews'        : reviews,
        'product_gallery': product_gallery,
    }

    return render(request, 'store/product_detail.html', context)


def search(request):
    products = []
    product_count = 0
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)