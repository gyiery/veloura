from django.contrib import admin
from .models import Coupon, Order, Product, Review
from .models import SupportTicket
from .models import Order
from .models import Coupon, Product, ProductImage, Review, Order, UserProfile, Address, SupportTicket
from .models import OrderRequest



class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
    'name',
    'category',
    'subcategory',
    'gender',
    'accessory_type',
    'price',
    'stock',
    'is_on_sale',
    'sale_percent',
    'is_new_arrival',
    'is_best_seller',
    ]

    list_filter = [
    'category',
    'subcategory',
    'gender',
    'accessory_type',
    'is_on_sale',
    'is_new_arrival',
    'is_best_seller',
    ]


    search_fields = ['name', 'description']
    inlines = [ProductImageInline]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'payment_status', 'order_status', 'total_amount', 'created_at')
    list_filter = ('order_status', 'payment_status')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['product__name', 'user__username', 'comment']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'minimum_order_amount', 'is_active')
    search_fields = ('code',)
    list_filter = ('discount_type', 'is_active')

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'subject')

@admin.register(OrderRequest)
class OrderRequestAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'request_type', 'status', 'created_at')
    list_filter = ('request_type', 'status')
    search_fields = ('order__id', 'user__username', 'reason')