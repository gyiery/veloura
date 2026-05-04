from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from products import views
from products.views import create_ticket

from products.views import (
    home,
    category_products,
    order_history,
    order_detail,
    account_page,
    product_detail,
    submit_review,
    add_to_cart,
    buy_now,
    check_pincode,
    cart_view,
    increase_cart_item,
    decrease_cart_item,
    remove_cart_item,
    search_products,
    wishlist_view,
    add_to_wishlist,
    checkout_view,
    place_order,
    order_success,
    create_razorpay_order,
    verify_razorpay_payment,
    payment_success,
    payment_cancel,
    apply_coupon,
    remove_coupon,
    dashboard_orders,
    dashboard_update_order_status,
    dashboard_support_tickets,
    dashboard_update_ticket,
)

from accounts.views import user_login, user_register, user_logout

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),

    path('category/<str:category_name>/', category_products, name='category_products'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('product/<int:product_id>/review/', submit_review, name='submit_review'),

    path('login/', user_login, name='login'),
    path('register/', user_register, name='register'),
    path('logout/', user_logout, name='logout'),
    path('account/', account_page, name='account_page'),

    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('buy-now/<int:product_id>/', buy_now, name='buy_now'),
    path('check-pincode/', check_pincode, name='check_pincode'),

    path('cart/', cart_view, name='cart'),
    path('cart/increase/<int:product_id>/', increase_cart_item, name='increase_cart_item'),
    path('cart/decrease/<int:product_id>/', decrease_cart_item, name='decrease_cart_item'),
    path('cart/remove/<int:product_id>/', remove_cart_item, name='remove_cart_item'),

    path('search/', search_products, name='search'),

    path('wishlist/', wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),

    path('checkout/', checkout_view, name='checkout'),
    path('place-order/', place_order, name='place_order'),
    path('order-success/', order_success, name='order_success'),

    path('payment/razorpay/create-order/', create_razorpay_order, name='create_razorpay_order'),
    path('payment/razorpay/verify/', verify_razorpay_payment, name='verify_razorpay_payment'),
    path('payment/success/', payment_success, name='payment_success'),
    path('payment/cancel/', payment_cancel, name='payment_cancel'),

    path('my-orders/', order_history, name='order_history'),
    path('my-orders/<int:order_id>/', order_detail, name='order_detail'),

    path('chatbot/ask/', views.chatbot_ask, name='chatbot_ask'),

    path('dashboard/', views.dashboard_overview, name='dashboard_overview'),
    path('dashboard/products/', views.dashboard_products, name='dashboard_products'),
    path('dashboard/products/add/', views.dashboard_add_product, name='dashboard_add_product'),
    path('dashboard/products/edit/<int:product_id>/', views.dashboard_edit_product, name='dashboard_edit_product'),
    path('dashboard/products/delete/<int:product_id>/', views.dashboard_delete_product, name='dashboard_delete_product'),
    path('dashboard/orders/', views.dashboard_orders, name='dashboard_orders'),
    path('dashboard/reviews/', views.dashboard_reviews, name='dashboard_reviews'),

    path('checkout/apply-coupon/', apply_coupon, name='apply_coupon'),
    path('checkout/remove-coupon/', remove_coupon, name='remove_coupon'),

    path('account/support/create/', create_ticket, name='create_ticket'),

    path('dashboard/orders/update-status/<int:order_id>/', views.dashboard_update_order_status, name='dashboard_update_order_status'),

    path('dashboard/support/', views.dashboard_support_tickets, name='dashboard_support_tickets'),
    path('dashboard/support/update/<int:ticket_id>/', views.dashboard_update_ticket, name='dashboard_update_ticket'),

    path('dashboard/coupons/', views.dashboard_coupons, name='dashboard_coupons'),
    path('dashboard/coupons/add/', views.dashboard_add_coupon, name='dashboard_add_coupon'),
    path('dashboard/coupons/edit/<int:coupon_id>/', views.dashboard_edit_coupon, name='dashboard_edit_coupon'),
    path('dashboard/coupons/delete/<int:coupon_id>/', views.dashboard_delete_coupon, name='dashboard_delete_coupon'),

    path('sale/', views.sale_products, name='sale_products'),

    path('order-request/<int:order_id>/', views.create_order_request, name='create_order_request'),

    path('dashboard/order-requests/', views.dashboard_order_requests, name='dashboard_order_requests'),
    path('dashboard/order-requests/update/<int:request_id>/', views.dashboard_update_order_request, name='dashboard_update_order_request'),

    path('recently-viewed/', views.recently_viewed_page, name='recently_viewed_page'),
    path('test-email/', views.test_email, name='test_email'),

    path('live-search/', views.live_search, name='live_search'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)