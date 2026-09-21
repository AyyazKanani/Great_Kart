from django.contrib import admin
from .models import Cart, CartItem

# Register your models here.

class CartAdmin(admin.ModelAdmin):
    list_diaplay = ('cart_id', 'date_added')

class CartItemAdmin(admin.ModelAdmin):
    list_diaplay = ('product', 'cart', 'quantity', 'is_active')

admin.site.register(Cart)
admin.site.register(CartItem, CartItemAdmin)