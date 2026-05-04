from itertools import product

from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Sum
from django.db.models.functions import TruncMonth
import razorpay
import json
import re

from urllib3 import request
from .models import Product, Order, OrderItem, Review, UserProfile, Address , Coupon
from django.contrib.auth.decorators import login_required
from .models import SupportTicket
from .models import Product, Order, OrderItem, Review, UserProfile, Address, Coupon, SupportTicket
from django.views.decorators.http import require_POST
from .models import Product, ProductImage, Order, OrderItem, OrderRequest, Review, UserProfile, Address, Coupon, SupportTicket

from django.core.mail import send_mail
from django.conf import settings

from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings


def home(request):
    perfume_products = Product.objects.filter(category='Perfume')[:8]
    featured_products = Product.objects.filter(is_best_seller=True)[:8]
    new_arrivals = Product.objects.filter(is_new_arrival=True)[:8]
    best_sellers = Product.objects.filter(is_best_seller=True)[:8]

    recent_ids = request.session.get('recently_viewed_products', [])
    recently_viewed_products = []

    if recent_ids:
        recent_products_qs = Product.objects.filter(id__in=recent_ids)
        recent_products_map = {str(product.id): product for product in recent_products_qs}

        for pid in recent_ids:
            if pid in recent_products_map:
                recently_viewed_products.append(recent_products_map[pid])

    context = {
        'perfume_products': perfume_products,
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'best_sellers': best_sellers,
        'recently_viewed_products': recently_viewed_products,
    }

    return render(request, 'home.html', context)


def category_products(request, category_name):
    category_map = {
        'women': ('Women', 'Women'),
        'men': ('Men', 'Men'),
        'kids': ('Kids', 'Kids'),
        'home': ('Home', 'Accessories'),
        'accessories': ('Home', 'Accessories'),
        'perfume': ('Perfume', 'Perfume'),
    }

    gender_map = {
        'men': 'Men',
        'women': 'Women',
    }

    accessory_type_map = {
        'shoes': 'Shoes',
        'watches': 'Watches',
        'glasses': 'Glasses',
        'belts': 'Belts',
        'wallets': 'Wallets',
        'purse': 'Purse',
        'jewellery': 'Jewellery',
        'skin-care': 'Skin-Care',
    }

    subcategory_map = {
        'shirts': 'Shirts',
        't-shirts': 'T-Shirts',
        'jeans': 'Jeans',
        'formal': 'Formal',
        'polos': 'Polos',
        'jackets': 'Jackets',
        'trousers': 'Trousers',
        'dresses': 'Dresses',
        'tops': 'Tops',
        'kurtas': 'Kurtas',
        'sarees': 'Sarees',
        'skirts': 'Skirts',
        'co-ords': 'Co-ords',
        'leggings': 'Leggings',
        'boys-wear': 'Boys Wear',
        'girls-wear': 'Girls Wear',
        'sets': 'Sets',
        'nightwear': 'Nightwear',
        'baby-wear': 'Baby Wear',
    }

    category_data = category_map.get(category_name.lower())
    if not category_data:
        return redirect('/')

    actual_category, display_category = category_data
    products = Product.objects.filter(category=actual_category)

    selected_gender = request.GET.get('gender', '').strip().lower()
    selected_type = request.GET.get('type', '').strip().lower()
    selected_subcategory = request.GET.get('subcategory', '').strip().lower()
    selected_sort = request.GET.get('sort', '').strip()

    if actual_category == 'Home':
        if selected_gender in gender_map:
            products = products.filter(gender=gender_map[selected_gender])

        if selected_type in accessory_type_map:
            products = products.filter(accessory_type=accessory_type_map[selected_type])

    if actual_category in ['Men', 'Women', 'Kids']:
        if selected_subcategory in subcategory_map:
            products = products.filter(subcategory=subcategory_map[selected_subcategory])

    if selected_sort == 'low-high':
        products = products.order_by('price')
    elif selected_sort == 'high-low':
        products = products.order_by('-price')
    elif selected_sort == 'newest':
        products = products.order_by('-id')

    context = {
        'products': products,
        'category_name': display_category,
        'selected_sort': selected_sort,
        'selected_gender': selected_gender,
        'selected_type': selected_type,
        'selected_subcategory': selected_subcategory,
    }
    return render(request, 'category.html', context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    gallery_images = product.gallery_images.all()

    review_stats = product.reviews.aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id')
    )

    average_rating = review_stats['avg_rating'] or 0
    total_reviews = review_stats['total_reviews'] or 0

    reviews = product.reviews.select_related('user')
    user_review = None

    if request.user.is_authenticated:
        user_review = Review.objects.filter(product=product, user=request.user).first()

    recent_ids = request.session.get('recently_viewed_products', [])

    product_id_str = str(product.id)
    if product_id_str in recent_ids:
        recent_ids.remove(product_id_str)

    recent_ids.insert(0, product_id_str)
    recent_ids = recent_ids[:8]

    request.session['recently_viewed_products'] = recent_ids
    request.session.modified = True

    context = {
        'product': product,
        'related_products': related_products,
        'gallery_images': gallery_images,
        'average_rating': round(average_rating, 1) if average_rating else 0,
        'total_reviews': total_reviews,
        'reviews': reviews,
        'user_review': user_review,
    }
    return render(request, 'product_detail.html', context)


def recently_viewed_page(request):
    recent_ids = request.session.get('recently_viewed_products', [])
    products = []

    if recent_ids:
        qs = Product.objects.filter(id__in=recent_ids)
        product_map = {str(p.id): p for p in qs}

        for pid in recent_ids:
            if pid in product_map:
                products.append(product_map[pid])

    return render(request, 'recently_viewed.html', {
        'products': products
    })


@login_required
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        try:
            rating = int(request.POST.get("rating"))
        except (TypeError, ValueError):
            rating = 0

        comment = request.POST.get("comment", "").strip()

        if rating < 1 or rating > 5:
            messages.error(request, "Please select a valid rating.")
            return redirect('product_detail', product_id=product.id)

        review, created = Review.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={
                'rating': rating,
                'comment': comment,
            }
        )

        if created:
            messages.success(request, "Your review has been submitted.")
        else:
            messages.success(request, "Your review has been updated.")

    return redirect('product_detail', product_id=product.id)


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.stock <= 0:
        messages.error(request, "This product is currently out of stock.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    quantity = 1
    if request.method == "POST":
        try:
            quantity = int(request.POST.get("quantity", 1))
            if quantity < 1:
                quantity = 1
        except (TypeError, ValueError):
            quantity = 1

    if quantity > product.stock:
        quantity = product.stock

    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        new_quantity = cart[product_id_str]['quantity'] + quantity
        cart[product_id_str]['quantity'] = min(new_quantity, product.stock)
    else:
        cart[product_id_str] = {
            'name': product.name,
            'price': float(product.price),
            'image': product.image.url if product.image else '',
            'category': product.category,
            'quantity': quantity,
            'detail_url': f'/product/{product.id}/',
            'stock': product.stock,
        }

    request.session['cart'] = cart
    request.session.modified = True

    messages.success(request, f"{product.name} added to cart.")
    return redirect(request.META.get('HTTP_REFERER', '/'))


def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.stock <= 0:
        messages.error(request, "This product is currently out of stock.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    quantity = 1
    if request.method == "POST":
        try:
            quantity = int(request.POST.get("quantity", 1))
            if quantity < 1:
                quantity = 1
        except (TypeError, ValueError):
            quantity = 1

    quantity = min(quantity, product.stock)

    request.session['cart'] = {
        str(product.id): {
            'name': product.name,
            'price': float(product.price),
            'image': product.image.url if product.image else '',
            'category': product.category,
            'quantity': quantity,
            'detail_url': f'/product/{product.id}/',
            'stock': product.stock,
        }
    }
    request.session.modified = True

    return redirect('checkout')


def check_pincode(request):
    pincode = request.GET.get("pincode", "").strip()

    if not pincode.isdigit() or len(pincode) != 6:
        return JsonResponse({
            "success": False,
            "message": "Please enter a valid 6-digit pincode."
        })

    last_digit = int(pincode[-1])

    if last_digit in [0, 1]:
        return JsonResponse({
            "success": True,
            "message": "Delivery available in 5-7 business days. COD may be limited for this pincode."
        })
    elif last_digit in [2, 3, 4, 5]:
        return JsonResponse({
            "success": True,
            "message": "Delivery available in 3-5 business days with secure prepaid checkout."
        })
    else:
        return JsonResponse({
            "success": True,
            "message": "Express delivery available in 2-4 business days for this pincode."
        })


def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    grand_total = 0

    for product_id, item in list(cart.items()):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            del cart[product_id]
            continue

        if item['quantity'] > product.stock:
            item['quantity'] = product.stock
            if item['quantity'] <= 0:
                del cart[product_id]
                continue

        subtotal = item['price'] * item['quantity']
        grand_total += subtotal

        cart_items.append({
            'id': product_id,
            'name': item['name'],
            'price': item['price'],
            'image': item['image'],
            'category': item['category'],
            'quantity': item['quantity'],
            'subtotal': subtotal,
            'detail_url': item.get('detail_url', f'/product/{product_id}/'),
            'stock': product.stock,
            'in_stock': product.stock > 0,
        })

    request.session['cart'] = cart
    request.session.modified = True

    context = {
        'cart_items': cart_items,
        'grand_total': grand_total,
    }

    return render(request, 'cart.html', context)


def calculate_cart_total(cart):
    total = 0
    for item in cart.values():
        total += item['price'] * item['quantity']
    return total


def get_coupon_discount(coupon, subtotal):
    if not coupon or not coupon.is_active:
        return 0

    if subtotal < float(coupon.minimum_order_amount):
        return 0

    if coupon.discount_type == 'flat':
        return min(float(coupon.discount_value), subtotal)

    if coupon.discount_type == 'percent':
        return round((subtotal * float(coupon.discount_value)) / 100, 2)

    return 0


def increase_cart_item(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        product = get_object_or_404(Product, id=product_id)
        current_qty = cart[product_id_str]['quantity']

        if current_qty < product.stock:
            cart[product_id_str]['quantity'] += 1
            cart[product_id_str]['stock'] = product.stock
            request.session['cart'] = cart
            request.session.modified = True
        else:
            messages.error(request, "You cannot add more than available stock.")

    return redirect('/cart/')


def decrease_cart_item(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        cart[product_id_str]['quantity'] -= 1

        if cart[product_id_str]['quantity'] <= 0:
            del cart[product_id_str]

        request.session['cart'] = cart
        request.session.modified = True

    return redirect('/cart/')


def remove_cart_item(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        request.session.modified = True

    return redirect('/cart/')


def search_products(request):
    query = request.GET.get('q')
    sort = request.GET.get('sort')
    results = Product.objects.none()

    if query:
        results = Product.objects.filter(name__icontains=query) | Product.objects.filter(category__icontains=query) | Product.objects.filter(description__icontains=query)

        if sort == 'low-high':
            results = results.order_by('price')
        elif sort == 'high-low':
            results = results.order_by('-price')
        elif sort == 'newest':
            results = results.order_by('-id')

    context = {
        'query': query,
        'results': results,
        'selected_sort': sort,
    }
    return render(request, 'search.html', context)


def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    wishlist = request.session.get('wishlist', {})
    product_id_str = str(product_id)

    if product_id_str in wishlist:
        del wishlist[product_id_str]
    else:
        wishlist[product_id_str] = {
            'name': product.name,
            'price': float(product.price),
            'image': product.image.url if product.image else '',
            'category': product.category,
        }

    request.session['wishlist'] = wishlist
    request.session.modified = True
    return redirect(request.META.get('HTTP_REFERER', '/'))


def wishlist_view(request):
    wishlist = request.session.get('wishlist', {})
    items = []

    for product_id, item in wishlist.items():
        items.append({
            'id': product_id,
            'name': item['name'],
            'price': item['price'],
            'image': item['image'],
            'category': item['category'],
            'detail_url': f'/product/{product_id}/',
        })

    return render(request, 'wishlist.html', {'items': items})


def apply_coupon(request):
    if request.method != "POST":
        return redirect('checkout')

    code = request.POST.get('coupon_code', '').strip().upper()
    cart = request.session.get('cart', {})

    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('checkout')

    if not code:
        messages.error(request, "Please enter a coupon code.")
        return redirect('checkout')

    try:
        coupon = Coupon.objects.get(code__iexact=code, is_active=True)
    except Coupon.DoesNotExist:
        messages.error(request, "Invalid or inactive coupon code.")
        return redirect('checkout')

    subtotal = calculate_cart_total(cart)

    if subtotal < float(coupon.minimum_order_amount):
        messages.error(
            request,
            f"This coupon requires a minimum order of ₹{coupon.minimum_order_amount}."
        )
        return redirect('checkout')

    discount = get_coupon_discount(coupon, subtotal)

    if discount <= 0:
        messages.error(request, "This coupon could not be applied.")
        return redirect('checkout')

    request.session['applied_coupon_code'] = coupon.code.upper()
    request.session.modified = True
    messages.success(request, f"Coupon {coupon.code.upper()} applied successfully.")
    return redirect('checkout')


def remove_coupon(request):
    if 'applied_coupon_code' in request.session:
        del request.session['applied_coupon_code']
        request.session.modified = True
        messages.success(request, "Coupon removed.")

    return redirect('checkout')


def checkout_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    subtotal = 0

    for product_id, item in cart.items():
        subtotal_item = item['price'] * item['quantity']
        subtotal += subtotal_item

        cart_items.append({
            'id': product_id,
            'name': item['name'],
            'price': item['price'],
            'image': item['image'],
            'quantity': item['quantity'],
            'subtotal': subtotal_item,
            'detail_url': item.get('detail_url', f'/product/{product_id}/'),
        })

    default_address = None
    checkout_prefill = {
        'full_name': '',
        'phone': '',
        'email': '',
        'address': '',
    }

    if request.user.is_authenticated:
        default_address = Address.objects.filter(user=request.user, is_default=True).first()

        if not default_address:
            default_address = Address.objects.filter(user=request.user).order_by('-created_at').first()

        checkout_prefill['email'] = request.user.email or ''

        if default_address:
            checkout_prefill['full_name'] = default_address.full_name or ''
            checkout_prefill['phone'] = default_address.phone or ''
            checkout_prefill['address'] = default_address.full_address or ''

    applied_coupon = None
    discount_amount = 0

    coupon_code = request.session.get('applied_coupon_code')
    if coupon_code:
        try:
            applied_coupon = Coupon.objects.get(code__iexact=coupon_code, is_active=True)
            discount_amount = get_coupon_discount(applied_coupon, subtotal)

            if discount_amount <= 0:
                applied_coupon = None
                if 'applied_coupon_code' in request.session:
                    del request.session['applied_coupon_code']
                    request.session.modified = True
        except Coupon.DoesNotExist:
            if 'applied_coupon_code' in request.session:
                del request.session['applied_coupon_code']
                request.session.modified = True

    total = max(subtotal - discount_amount, 0)

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount_amount': discount_amount,
        'total': total,
        'default_address': default_address,
        'checkout_prefill': checkout_prefill,
        'applied_coupon': applied_coupon,
    }
    return render(request, 'checkout.html', context)


def place_order(request):
    return redirect('checkout')


def order_success(request):
    return redirect('payment_success')


@csrf_exempt
def create_razorpay_order(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    cart = request.session.get('cart', {})
    if not cart:
        return JsonResponse({'error': 'Cart empty'}, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    full_name = (data.get('full_name') or '').strip()
    phone = (data.get('phone') or '').strip()
    email = (data.get('email') or '').strip()
    address = (data.get('address') or '').strip()

    if not full_name:
        return JsonResponse({'error': 'Full name is required.'}, status=400)

    if not phone or not phone.isdigit() or len(phone) < 10:
        return JsonResponse({'error': 'Enter a valid phone number.'}, status=400)

    if email and '@' not in email:
        return JsonResponse({'error': 'Enter a valid email address.'}, status=400)

    if not address or len(address) < 10:
        return JsonResponse({'error': 'Enter a complete delivery address.'}, status=400)

    subtotal = 0
    validated_items = []

    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'error': f'{item["name"]} is no longer available.'}, status=400)

        if product.stock <= 0:
            return JsonResponse({'error': f'{product.name} is out of stock.'}, status=400)

        if item['quantity'] > product.stock:
            return JsonResponse({'error': f'Only {product.stock} item(s) available for {product.name}.'}, status=400)

        subtotal += item['price'] * item['quantity']
        validated_items.append((product, item))

    applied_coupon = None
    discount_amount = 0

    coupon_code = request.session.get('applied_coupon_code')
    if coupon_code:
        try:
            applied_coupon = Coupon.objects.get(code__iexact=coupon_code, is_active=True)
            discount_amount = get_coupon_discount(applied_coupon, subtotal)
        except Coupon.DoesNotExist:
            discount_amount = 0

    final_total = max(subtotal - discount_amount, 0)
    total_paise = int(final_total * 100)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    razorpay_order = client.order.create({
        "amount": total_paise,
        "currency": "INR",
        "payment_capture": 1
    })

    from datetime import date, timedelta
    estimated_delivery = date.today() + timedelta(days=5)

    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        full_name=full_name,
        email=email if email else None,
        phone=phone,
        address=address,
        total_amount=final_total,
        payment_provider="razorpay",
        payment_status="created",
        gateway_order_id=razorpay_order['id'],
        order_status='placed',
        estimated_delivery=estimated_delivery
    )

    for product, item in validated_items:
        OrderItem.objects.create(
            order=order,
            product_name=item['name'],
            price=item['price'],
            quantity=item['quantity'],
            image=item['image']
        )

    return JsonResponse({
        "razorpay_order_id": razorpay_order['id'],
        "amount": total_paise,
        "key": settings.RAZORPAY_KEY_ID,
        "customer_name": full_name,
        "customer_email": email,
        "customer_phone": phone,
        "order_db_id": order.id
    })


@csrf_exempt
def verify_razorpay_payment(request):
    if request.method != "POST":
        return redirect('payment_cancel')

    data = request.POST
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': data.get('razorpay_order_id'),
            'razorpay_payment_id': data.get('razorpay_payment_id'),
            'razorpay_signature': data.get('razorpay_signature')
        })

        order = Order.objects.get(gateway_order_id=data.get('razorpay_order_id'))

        if order.payment_status != "paid":
            for item in order.items.all():
                product = Product.objects.filter(name=item.product_name).first()
                if product:
                    product.stock = max(product.stock - item.quantity, 0)
                    product.save()

        order.payment_status = "paid"
        order.gateway_payment_id = data.get('razorpay_payment_id')
        order.gateway_signature = data.get('razorpay_signature')
        order.is_verified = True
        order.save()

        send_order_confirmation_email(order)

        request.session['cart'] = {}
        if 'applied_coupon_code' in request.session:
            del request.session['applied_coupon_code']
        request.session.modified = True

        return redirect('order_history')

    except Exception:
        try:
            order = Order.objects.get(gateway_order_id=data.get('razorpay_order_id'))
            order.payment_status = "failed"
            order.gateway_payment_id = data.get('razorpay_payment_id')
            order.gateway_signature = data.get('razorpay_signature')
            order.save()
        except Exception:
            pass

        return redirect('payment_cancel')


def payment_success(request):
    if request.user.is_authenticated:
        latest_order = Order.objects.filter(user=request.user, payment_status="paid").order_by('-created_at').first()
    else:
        latest_order = Order.objects.filter(payment_status="paid").order_by('-created_at').first()

    context = {'order': latest_order}
    return render(request, 'order_success.html', context)


def payment_cancel(request):
    return render(request, 'payment_failed.html')


def order_history(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'order_history.html', {
        'user_orders': user_orders
    })


def order_detail(request, order_id):
    if not request.user.is_authenticated:
        return redirect('login')

    order = get_object_or_404(Order, id=order_id, user=request.user)

    return render(request, 'order_detail.html', {
        'order': order
    })


@login_required
def account_page(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    active_tab = request.GET.get('tab', 'profile')

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "profile_form":
            request.user.first_name = request.POST.get("first_name", "").strip()
            request.user.last_name = request.POST.get("last_name", "").strip()
            request.user.email = request.POST.get("email", "").strip()
            request.user.save()

            profile.phone = request.POST.get("phone", "").strip()
            profile.gender = request.POST.get("gender", "").strip() or None

            dob = request.POST.get("date_of_birth", "").strip()
            profile.date_of_birth = dob if dob else None

            if request.FILES.get("profile_image"):
                profile.profile_image = request.FILES.get("profile_image")

            profile.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('/account/?tab=profile')

        elif form_type == "address_form":
            address_id = request.POST.get("address_id", "").strip()

            if address_id:
                address = get_object_or_404(Address, id=address_id, user=request.user)
            else:
                address = Address(user=request.user)

            address.full_name = request.POST.get("address_full_name", "").strip()
            address.phone = request.POST.get("address_phone", "").strip()
            address.address_line_1 = request.POST.get("address_line_1", "").strip()
            address.address_line_2 = request.POST.get("address_line_2", "").strip()
            address.city = request.POST.get("city", "").strip()
            address.state = request.POST.get("state", "").strip()
            address.postal_code = request.POST.get("postal_code", "").strip()
            address.country = request.POST.get("country", "India").strip() or "India"

            is_default = request.POST.get("is_default") == "on"

            if is_default:
                Address.objects.filter(user=request.user).update(is_default=False)
                address.is_default = True
            elif not Address.objects.filter(user=request.user).exists():
                address.is_default = True

            address.save()
            messages.success(request, "Address saved successfully.")
            return redirect('/account/?tab=addresses')

        elif form_type == "delete_address":
            address_id = request.POST.get("delete_address_id")
            address = get_object_or_404(Address, id=address_id, user=request.user)
            address.delete()
            messages.success(request, "Address deleted successfully.")
            return redirect('/account/?tab=addresses')

        elif form_type == "set_default_address":
            address_id = request.POST.get("default_address_id")
            address = get_object_or_404(Address, id=address_id, user=request.user)
            Address.objects.filter(user=request.user).update(is_default=False)
            address.is_default = True
            address.save()
            messages.success(request, "Default address updated.")
            return redirect('/account/?tab=addresses')

    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    wishlist = request.session.get('wishlist', {})
    wishlist_items = []

    order_requests = OrderRequest.objects.filter(user=request.user).select_related('order').order_by('-created_at')

    for product_id, item in wishlist.items():
        wishlist_items.append({
            'id': product_id,
            'name': item['name'],
            'price': item['price'],
            'image': item['image'],
            'category': item['category'],
            'detail_url': f'/product/{product_id}/',
        })

    addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-created_at')

    context = {
        'active_tab': active_tab,
        'user_orders': user_orders,
        'wishlist_items': wishlist_items,
        'addresses': addresses,
        'profile': profile,
        'order_requests': order_requests,
    }
    return render(request, 'account_page.html', context)


@csrf_exempt
def chatbot_ask(request):
    if request.method != "POST":
        return JsonResponse({"reply": "Invalid request."}, status=400)

    try:
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()
        user_name = data.get("name", "").strip()
    except Exception:
        return JsonResponse({"reply": "Invalid input."}, status=400)

    if not user_message:
        return JsonResponse({"reply": "Please type your question."})

    msg = re.sub(r"\s+", " ", user_message.lower()).strip()

    chat_memory = request.session.get("chat_memory", [])
    chat_memory.append({"role": "user", "message": user_message})
    chat_memory = chat_memory[-8:]
    request.session["chat_memory"] = chat_memory
    request.session.modified = True

    def make_response(reply, buttons=None, products=None):
        bot_entry = {"role": "bot", "message": reply}
        memory = request.session.get("chat_memory", [])
        memory.append(bot_entry)
        request.session["chat_memory"] = memory[-8:]
        request.session.modified = True

        return JsonResponse({
            "reply": reply,
            "buttons": buttons or [],
            "products": products or []
        })

    def contains_any(text, keywords):
        return any(keyword in text for keyword in keywords)

    def product_cards(queryset, limit=4):
        items = []
        for p in queryset[:limit]:
            items.append({
                "id": p.id,
                "name": p.name,
                "price": str(p.price),
                "url": f"/product/{p.id}/",
                "image": p.image.url if p.image else "",
                "category": p.category
            })
        return items

    def strict_fallback():
        return make_response(
            "Sorry, I can only help with Veloura website-related questions like products, perfumes, categories, cart, wishlist, checkout, payment, delivery, returns, login, and orders.",
            buttons=["Show Products", "Best Products", "New Arrivals", "Perfumes"]
        )

    def product_reply(queryset, intro, empty_text, buttons=None):
        if queryset.exists():
            return make_response(
                intro,
                buttons=buttons or ["Best Products", "New Arrivals", "Perfumes"],
                products=product_cards(queryset)
            )
        return make_response(
            empty_text,
            buttons=buttons or ["Show Products", "Best Products", "Perfumes"]
        )

    def get_recent_preference():
        memory = request.session.get("chat_memory", [])
        joined = " ".join([m["message"].lower() for m in memory if m["role"] == "user"])
        if "perfume" in joined or "attar" in joined or "fragrance" in joined:
            return "Perfume"
        if "women" in joined:
            return "Women"
        if "men" in joined:
            return "Men"
        if "kids" in joined:
            return "Kids"
        if "accessories" in joined or "watch" in joined or "watches" in joined or "glasses" in joined or "sunglasses" in joined or "belt" in joined or "wallet" in joined or "bag" in joined:
            return "Home"
        return None

    blocked_topics = [
        "weather", "news", "politics", "prime minister", "president",
        "movie", "film", "song", "music", "cricket", "football",
        "joke", "python", "java", "programming", "coding", "science",
        "history", "geography", "math", "medical", "doctor", "disease",
        "bitcoin", "crypto", "stock market", "relationship", "girlfriend",
        "boyfriend", "astrology", "religion",
    ]
    if contains_any(msg, blocked_topics):
        return strict_fallback()

    if contains_any(msg, ["hi", "hello", "hey", "hii", "helo"]):
        welcome_name = f" {user_name}" if user_name else ""
        return make_response(
            f"Hello{welcome_name} ✨ Welcome to Veloura. I can help you with products, perfumes, shopping, payments, orders, and support.",
            buttons=["Show Products", "Best Products", "New Arrivals", "Perfumes"]
        )

    if contains_any(msg, [
        "products", "product", "what do you sell", "which products",
        "what products", "items", "collection", "show products",
        "show me products", "what does veloura sell"
    ]):
        return product_reply(
            Product.objects.all(),
            "Here are some products available on Veloura:",
            "Currently, no products are available on Veloura."
        )

    if contains_any(msg, [
        "best", "best product", "best products", "top", "top products",
        "popular", "popular products", "best seller", "best sellers",
        "top selling", "show best products"
    ]):
        return product_reply(
            Product.objects.filter(is_best_seller=True),
            "These are our best products on Veloura:",
            "Currently, no best seller products are available.",
            buttons=["New Arrivals", "Perfumes", "Show Products"]
        )

    if contains_any(msg, [
        "new", "latest", "new products", "latest products",
        "new arrival", "new arrivals", "latest items"
    ]):
        return product_reply(
            Product.objects.filter(is_new_arrival=True),
            "These are our latest arrivals:",
            "Currently, no new arrival products are available.",
            buttons=["Best Products", "Perfumes", "Show Products"]
        )

    if contains_any(msg, ["perfume", "perfumes", "attar", "fragrance", "scent"]):
        return product_reply(
            Product.objects.filter(category="Perfume"),
            "Here is our perfume collection:",
            "Currently, no perfume products are available on Veloura.",
            buttons=["Best Products", "New Arrivals", "Show Products"]
        )

    if contains_any(msg, ["women", "women products", "women collection", "ladies"]):
        return product_reply(
            Product.objects.filter(category="Women"),
            "Here are products from our Women collection:",
            "Currently, no Women products are available.",
            buttons=["Men Products", "Perfumes", "Best Products"]
        )

    if contains_any(msg, ["men", "men products", "men collection", "menswear"]):
        return product_reply(
            Product.objects.filter(category="Men"),
            "Here are products from our Men collection:",
            "Currently, no Men products are available.",
            buttons=["Women Products", "Perfumes", "Best Products"]
        )

    if contains_any(msg, ["kids", "kid", "kids products", "kids collection"]):
        return product_reply(
            Product.objects.filter(category="Kids"),
            "Here are products from our Kids collection:",
            "Currently, no Kids products are available.",
            buttons=["Women Products", "Men Products", "Best Products"]
        )

    if contains_any(msg, ["accessories", "accessory", "watches", "watch", "glasses", "sunglasses", "wallet", "wallets", "belt", "belts", "bags", "jewellery"]):
        return product_reply(
            Product.objects.filter(category="Home"),
            "Here are products from our Accessories collection:",
            "Currently, no Accessories products are available.",
            buttons=["Show Products", "Best Products", "Perfumes"]
        )

    if contains_any(msg, ["price", "cost", "how much"]):
        matched = Product.objects.filter(name__icontains=user_message)[:3]
        if matched.exists():
            text = "Here are the matching prices: " + ", ".join(
                [f"{p.name} - ₹{p.price}" for p in matched]
            ) + "."
            return make_response(
                text,
                buttons=["Show Products", "Best Products", "Checkout Help"]
            )
        return make_response(
            "Please mention the exact product name to check its price.",
            buttons=["Show Products", "Best Products", "Perfumes"]
        )

    if contains_any(msg, ["show", "find", "search", "looking for", "do you have", "have"]):
        matched = Product.objects.filter(name__icontains=user_message)
        if matched.exists():
            return product_reply(
                matched,
                "I found these matching products:",
                "No matching products were found on Veloura.",
                buttons=["Best Products", "New Arrivals", "Perfumes"]
            )

    if contains_any(msg, ["recommend", "suggest", "recommended", "what should i buy"]):
        preference = get_recent_preference()

        if preference:
            qs = Product.objects.filter(category=preference)
            if preference == "Perfume":
                title = "Based on your interest, I recommend these perfumes:"
            elif preference == "Home":
                title = "Based on your interest, I recommend these accessories:"
            else:
                title = f"Based on your interest, I recommend these {preference.lower()} products:"
            return product_reply(
                qs,
                title,
                "I could not find matching recommended products right now.",
                buttons=["Best Products", "New Arrivals", "Perfumes"]
            )

        return product_reply(
            Product.objects.filter(is_best_seller=True),
            "Here are some recommended products from Veloura:",
            "No recommended products are available right now.",
            buttons=["Perfumes", "Best Products", "New Arrivals"]
        )

    if contains_any(msg, ["cart", "add to cart"]):
        return make_response(
            "You can add products to your cart from the product card or product detail page, then review them on the cart page.",
            buttons=["Checkout Help", "Show Products", "Best Products"]
        )

    if "wishlist" in msg:
        return make_response(
            "You can save products to your wishlist and view them later from the wishlist page.",
            buttons=["Show Products", "Best Products", "Perfumes"]
        )

    if "checkout" in msg:
        return make_response(
            "You can proceed to checkout from the cart page after adding your products.",
            buttons=["Payment Help", "Delivery Help", "Show Products"]
        )

    if contains_any(msg, ["payment", "pay", "online payment"]):
        return make_response(
            "Veloura supports secure payment during checkout. Please proceed from the cart page to the checkout page to complete your order.",
            buttons=["Checkout Help", "Delivery Help", "Show Products"]
        )

    if "razorpay" in msg:
        return make_response(
            "Veloura supports Razorpay for secure online payment during checkout.",
            buttons=["Checkout Help", "Payment Help"]
        )

    if contains_any(msg, ["cod", "cash on delivery"]):
        return make_response(
            "Cash on Delivery depends on the checkout option currently available on Veloura.",
            buttons=["Checkout Help", "Payment Help"]
        )

    if contains_any(msg, ["shipping", "delivery"]):
        return make_response(
            "Shipping and delivery details are completed during checkout when you enter your address and place the order.",
            buttons=["Checkout Help", "Payment Help"]
        )

    if contains_any(msg, ["return", "refund", "exchange"]):
        return make_response(
            "For return, refund, or exchange help, please contact Veloura support with your order details.",
            buttons=["Order Help", "Support Help"]
        )

    if contains_any(msg, ["order", "my order", "my orders", "track order", "order history"]):
        if request.user.is_authenticated:
            user_orders = Order.objects.filter(user=request.user).order_by("-created_at")[:3]
            if user_orders.exists():
                text = "Your recent orders: " + ", ".join(
                    [f"Order #{o.id} ({o.payment_status})" for o in user_orders]
                ) + "."
                return make_response(
                    text,
                    buttons=["Payment Help", "Delivery Help", "Support Help"]
                )
            return make_response(
                "I could not find any recent orders for your logged-in account.",
                buttons=["Show Products", "Best Products", "Support Help"]
            )

        return make_response(
            "Please log in to view your order history and order-related details.",
            buttons=["Login Help", "Show Products", "Support Help"]
        )

    if contains_any(msg, ["login", "sign in"]):
        return make_response(
            "You can log in from the login page to access your account, wishlist, and orders.",
            buttons=["Register Help", "Order Help", "Show Products"]
        )

    if contains_any(msg, ["register", "signup", "sign up", "create account"]):
        return make_response(
            "You can create a new account from the register page on Veloura.",
            buttons=["Login Help", "Show Products"]
        )

    if contains_any(msg, ["help", "support"]):
        return make_response(
            "I can help with Veloura products, categories, perfumes, cart, wishlist, checkout, payment, delivery, returns, account, and orders.",
            buttons=["Show Products", "Best Products", "Order Help", "Perfumes"]
        )

    if msg == "show products":
        return product_reply(
            Product.objects.all(),
            "Here are some products available on Veloura:",
            "Currently, no products are available on Veloura."
        )

    if msg == "best products":
        return product_reply(
            Product.objects.filter(is_best_seller=True),
            "These are our best products on Veloura:",
            "Currently, no best seller products are available."
        )

    if msg == "new arrivals":
        return product_reply(
            Product.objects.filter(is_new_arrival=True),
            "These are our latest arrivals:",
            "Currently, no new arrival products are available."
        )

    if msg == "perfumes":
        return product_reply(
            Product.objects.filter(category="Perfume"),
            "Here is our perfume collection:",
            "Currently, no perfume products are available on Veloura."
        )

    if msg == "checkout help":
        return make_response(
            "You can proceed to checkout from the cart page after adding your products.",
            buttons=["Payment Help", "Delivery Help"]
        )

    if msg == "payment help":
        return make_response(
            "Veloura supports secure payment during checkout.",
            buttons=["Checkout Help", "Delivery Help"]
        )

    if msg == "delivery help":
        return make_response(
            "Shipping and delivery details are completed during checkout when you enter your address and place the order.",
            buttons=["Checkout Help", "Payment Help"]
        )

    if msg == "order help":
        if request.user.is_authenticated:
            user_orders = Order.objects.filter(user=request.user).order_by("-created_at")[:3]
            if user_orders.exists():
                text = "Your recent orders: " + ", ".join(
                    [f"Order #{o.id} ({o.payment_status})" for o in user_orders]
                ) + "."
                return make_response(text, buttons=["Payment Help", "Delivery Help", "Support Help"])
        return make_response(
            "Please log in to view your order history and order-related details.",
            buttons=["Login Help", "Support Help"]
        )

    if msg == "login help":
        return make_response(
            "You can log in from the login page to access your account, wishlist, and orders.",
            buttons=["Register Help", "Order Help"]
        )

    if msg == "register help":
        return make_response(
            "You can create a new account from the register page on Veloura.",
            buttons=["Login Help", "Show Products"]
        )

    if msg == "support help":
        return make_response(
            "I can help with Veloura products, categories, perfumes, cart, checkout, payment, delivery, returns, account, and orders.",
            buttons=["Show Products", "Best Products", "Perfumes"]
        )

    return strict_fallback()


@login_required
def dashboard_overview(request):
    if not request.user.is_superuser:
        return redirect('/')

    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_reviews = Review.objects.count()
    total_sales = Order.objects.filter(payment_status="paid").aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    recent_orders = Order.objects.order_by('-created_at')[:6]
    recent_products = Product.objects.order_by('-id')[:6]
    recent_reviews = Review.objects.select_related('product', 'user').order_by('-created_at')[:6]

    monthly_sales_qs = (
        Order.objects.filter(payment_status="paid")
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('total_amount'))
        .order_by('month')
    )

    sales_labels = []
    sales_data = []

    for item in monthly_sales_qs:
        sales_labels.append(item['month'].strftime('%b'))
        sales_data.append(float(item['total']))

    monthly_orders_qs = (
        Order.objects.annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )

    orders_labels = []
    orders_data = []

    for item in monthly_orders_qs:
        orders_labels.append(item['month'].strftime('%b'))
        orders_data.append(item['total'])

    category_map = {
        'Women': 'Women',
        'Men': 'Men',
        'Kids': 'Kids',
        'Home': 'Accessories',
        'Perfume': 'Perfume',
    }

    category_labels = []
    category_data = []

    for db_value, display_name in category_map.items():
        count = Product.objects.filter(category=db_value).count()
        category_labels.append(display_name)
        category_data.append(count)

    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_reviews': total_reviews,
        'total_sales': total_sales,
        'recent_orders': recent_orders,
        'recent_products': recent_products,
        'recent_reviews': recent_reviews,
        'sales_labels_json': json.dumps(sales_labels),
        'sales_data_json': json.dumps(sales_data),
        'orders_labels_json': json.dumps(orders_labels),
        'orders_data_json': json.dumps(orders_data),
        'category_labels_json': json.dumps(category_labels),
        'category_data_json': json.dumps(category_data),
    }
    return render(request, 'dashboard/overview.html', context)


@login_required
def dashboard_products(request):
    if not request.user.is_superuser:
        return redirect('/')

    selected_category = request.GET.get('category', '').strip()

    all_products = Product.objects.all().order_by('-id')

    if selected_category in ['Women', 'Men', 'Kids', 'Home', 'Perfume']:
        products = all_products.filter(category=selected_category)
    else:
        products = all_products
        selected_category = ''

    total_products = all_products.count()
    women_count = all_products.filter(category='Women').count()
    men_count = all_products.filter(category='Men').count()
    kids_count = all_products.filter(category='Kids').count()
    accessories_count = all_products.filter(category='Home').count()
    perfume_count = all_products.filter(category='Perfume').count()

    low_stock_products = products.filter(stock__gt=0, stock__lte=5).order_by('stock')
    out_of_stock_products = products.filter(stock=0)

    context = {
        'products': products,
        'selected_category': selected_category,

        'total_products': total_products,
        'women_count': women_count,
        'men_count': men_count,
        'kids_count': kids_count,
        'accessories_count': accessories_count,
        'perfume_count': perfume_count,

        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
    }
    return render(request, 'dashboard/products.html', context)


@login_required
def dashboard_add_product(request):
    if not request.user.is_superuser:
        return redirect('/')

    if request.method == "POST":
        name = request.POST.get("name")
        category = request.POST.get("category")
        price = request.POST.get("price")
        description = request.POST.get("description")
        image = request.FILES.get("image")
        stock = int(request.POST.get("stock", 0))

        is_on_sale = request.POST.get("is_on_sale") == "on"
        sale_percent = int(request.POST.get("sale_percent", 0))

        gender = request.POST.get("gender") or None
        accessory_type = request.POST.get("accessory_type") or None
        subcategory = request.POST.get("subcategory") or None

        is_new_arrival = request.POST.get("is_new_arrival") == "on"
        is_best_seller = request.POST.get("is_best_seller") == "on"

        Product.objects.create(
            name=name,
            category=category,
            price=price,
            description=description,
            image=image,
            gender=gender,
            accessory_type=accessory_type,
            subcategory=subcategory,
            is_new_arrival=is_new_arrival,
            is_best_seller=is_best_seller,
            stock=stock,
            is_on_sale=is_on_sale,
            sale_percent=sale_percent,
        )

        messages.success(request, "Product added successfully.")
        return redirect('dashboard_products')

    return render(request, 'dashboard/add_product.html')


@login_required
def dashboard_edit_product(request, product_id):
    if not request.user.is_superuser:
        return redirect('/')

    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.category = request.POST.get("category")
        product.price = request.POST.get("price")
        product.description = request.POST.get("description")
        product.gender = request.POST.get("gender") or None
        product.accessory_type = request.POST.get("accessory_type") or None
        product.subcategory = request.POST.get("subcategory") or None
        product.is_new_arrival = request.POST.get("is_new_arrival") == "on"
        product.is_best_seller = request.POST.get("is_best_seller") == "on"
        product.stock = int(request.POST.get("stock", 0))
        product.is_on_sale = request.POST.get("is_on_sale") == "on"
        product.sale_percent = int(request.POST.get("sale_percent", 0))

        if request.FILES.get("image"):
            product.image = request.FILES.get("image")

        product.save()
        messages.success(request, "Product updated successfully.")
        return redirect('dashboard_products')

    return render(request, 'dashboard/edit_product.html', {'product': product})


@login_required
def dashboard_delete_product(request, product_id):
    if not request.user.is_superuser:
        return redirect('/')

    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, "Product deleted successfully.")
    return redirect('dashboard_products')


@login_required
def dashboard_orders(request):
    if not request.user.is_superuser:
        return redirect('/')

    orders = Order.objects.all().prefetch_related('items').order_by('-created_at')
    return render(request, 'dashboard/orders.html', {'orders': orders})


@login_required
def dashboard_reviews(request):
    if not request.user.is_superuser:
        return redirect('/')

    reviews = Review.objects.select_related('product', 'user').order_by('-created_at')
    return render(request, 'dashboard/reviews.html', {'reviews': reviews})


def checkout_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, item in cart.items():
        subtotal = item['price'] * item['quantity']
        total += subtotal

        cart_items.append({
            'id': product_id,
            'name': item['name'],
            'price': item['price'],
            'image': item['image'],
            'quantity': item['quantity'],
            'subtotal': subtotal,
            'detail_url': item.get('detail_url', f'/product/{product_id}/'),
        })

    default_address = None
    checkout_prefill = {
        'full_name': '',
        'phone': '',
        'email': '',
        'address': '',
    }

    if request.user.is_authenticated:
        default_address = Address.objects.filter(
            user=request.user,
            is_default=True
        ).first()

        if not default_address:
            default_address = Address.objects.filter(user=request.user).order_by('-created_at').first()

        checkout_prefill['email'] = request.user.email or ''

        if default_address:
            checkout_prefill['full_name'] = default_address.full_name or ''
            checkout_prefill['phone'] = default_address.phone or ''
            checkout_prefill['address'] = default_address.full_address or ''

    context = {
        'cart_items': cart_items,
        'total': total,
        'default_address': default_address,
        'checkout_prefill': checkout_prefill,
    }
    return render(request, 'checkout.html', context)


@login_required
def create_ticket(request):
    if request.method == "POST":
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if subject and message:
            SupportTicket.objects.create(
                user=request.user,
                subject=subject,
                message=message
            )

        return redirect('/account/?tab=support')


@login_required
@require_POST
def dashboard_update_order_status(request, order_id):
    if not request.user.is_superuser:
        return redirect('/')

    order = get_object_or_404(Order, id=order_id)
    old_status = order.order_status
    new_status = request.POST.get('order_status')

    allowed_statuses = ['placed', 'packed', 'shipped', 'out_for_delivery', 'delivered', 'cancelled']

    if new_status in allowed_statuses:
        order.order_status = new_status
        order.save()
        messages.success(request, f"Order #{order.id} status updated to {order.get_order_status_display()}.")

        if old_status != 'shipped' and new_status == 'shipped':
            send_order_shipped_email(order)

    return redirect('dashboard_orders')


@login_required
def dashboard_support_tickets(request):
    if not request.user.is_superuser:
        return redirect('/')

    tickets = SupportTicket.objects.select_related('user').order_by('-created_at')

    context = {
        'tickets': tickets,
    }
    return render(request, 'dashboard/support_tickets.html', context)


@login_required
@require_POST
def dashboard_update_ticket(request, ticket_id):
    if not request.user.is_superuser:
        return redirect('/')

    ticket = get_object_or_404(SupportTicket, id=ticket_id)

    new_status = request.POST.get('status')
    admin_reply = request.POST.get('admin_reply', '').strip()

    allowed_statuses = ['open', 'in_progress', 'resolved']

    if new_status in allowed_statuses:
        ticket.status = new_status

    ticket.admin_reply = admin_reply
    ticket.save()

    messages.success(request, f"Support ticket '{ticket.subject}' updated successfully.")
    return redirect('dashboard_support_tickets')


@login_required
def dashboard_coupons(request):
    if not request.user.is_superuser:
        return redirect('/')

    coupons = Coupon.objects.all().order_by('-id')

    context = {
        'coupons': coupons,
    }
    return render(request, 'dashboard/coupons.html', context)


@login_required
def dashboard_add_coupon(request):
    if not request.user.is_superuser:
        return redirect('/')

    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        discount_type = request.POST.get('discount_type')
        discount_value = request.POST.get('discount_value')
        minimum_order_amount = request.POST.get('minimum_order_amount', 0)
        is_active = request.POST.get('is_active') == 'on'

        if code and discount_type and discount_value:
            Coupon.objects.create(
                code=code,
                discount_type=discount_type,
                discount_value=discount_value,
                minimum_order_amount=minimum_order_amount or 0,
                is_active=is_active,
            )
            messages.success(request, f"Coupon {code} created successfully.")
            return redirect('dashboard_coupons')

    return render(request, 'dashboard/add_coupon.html')


@login_required
def dashboard_edit_coupon(request, coupon_id):
    if not request.user.is_superuser:
        return redirect('/')

    coupon = get_object_or_404(Coupon, id=coupon_id)

    if request.method == 'POST':
        coupon.code = request.POST.get('code', '').strip().upper()
        coupon.discount_type = request.POST.get('discount_type')
        coupon.discount_value = request.POST.get('discount_value')
        coupon.minimum_order_amount = request.POST.get('minimum_order_amount', 0)
        coupon.is_active = request.POST.get('is_active') == 'on'
        coupon.save()

        messages.success(request, f"Coupon {coupon.code} updated successfully.")
        return redirect('dashboard_coupons')

    return render(request, 'dashboard/edit_coupon.html', {'coupon': coupon})


@login_required
def dashboard_delete_coupon(request, coupon_id):
    if not request.user.is_superuser:
        return redirect('/')

    coupon = get_object_or_404(Coupon, id=coupon_id)
    coupon.delete()
    messages.success(request, "Coupon deleted successfully.")
    return redirect('dashboard_coupons')


def sale_products(request):
    products = Product.objects.filter(is_on_sale=True, sale_percent__gt=0).order_by('-id')

    context = {
        'products': products,
        'page_title': 'Sale',
    }
    return render(request, 'sale.html', context)


@login_required
def create_order_request(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST':
        request_type = request.POST.get('request_type')
        reason = request.POST.get('reason', '').strip()

        if not reason:
            messages.error(request, "Please enter a reason.")
            return redirect('account_page')

        if request_type == 'cancel':
            if order.order_status not in ['placed', 'packed']:
                messages.error(request, "This order can no longer be cancelled.")
                return redirect('account_page')

        elif request_type == 'return':
            if order.order_status != 'delivered':
                messages.error(request, "Return request is only available after delivery.")
                return redirect('account_page')
        else:
            messages.error(request, "Invalid request type.")
            return redirect('account_page')

        existing_request = OrderRequest.objects.filter(
            order=order,
            user=request.user,
            request_type=request_type,
            status='pending'
        ).first()

        if existing_request:
            messages.error(request, "You already have a pending request for this order.")
            return redirect('account_page')

        OrderRequest.objects.create(
            order=order,
            user=request.user,
            request_type=request_type,
            reason=reason
        )

        messages.success(request, f"{request_type.title()} request submitted successfully.")
        return redirect('/account/?tab=orders')

    return redirect('/account/?tab=orders')


@login_required
def dashboard_order_requests(request):
    if not request.user.is_superuser:
        return redirect('/')

    order_requests = OrderRequest.objects.select_related('order', 'user').order_by('-created_at')

    context = {
        'order_requests': order_requests,
    }
    return render(request, 'dashboard/order_requests.html', context)


@login_required
@require_POST
def dashboard_update_order_request(request, request_id):
    if not request.user.is_superuser:
        return redirect('/')

    order_request = get_object_or_404(OrderRequest, id=request_id)
    old_status = order_request.status
    new_status = request.POST.get('status')
    admin_note = request.POST.get('admin_note', '').strip()

    if new_status in ['pending', 'approved', 'rejected']:
        order_request.status = new_status
        order_request.admin_note = admin_note
        order_request.save()

        if new_status == 'approved' and order_request.request_type == 'cancel':
            if order_request.order.order_status in ['placed', 'packed']:
                order_request.order.order_status = 'cancelled'
                order_request.order.save()

            if old_status != 'approved':
                send_cancel_approved_email(order_request)

        if new_status == 'approved' and order_request.request_type == 'return':
            if old_status != 'approved':
                send_return_approved_email(order_request)

        messages.success(request, "Order request updated successfully.")

    return redirect('dashboard_order_requests')


def send_order_confirmation_email(order):
    if not order.email:
        return

    subject = f"Veloura Order Confirmed - Order #{order.id}"
    message = f"""
Hello {order.full_name},

Your order #{order.id} has been confirmed successfully.

Order Total: ₹{order.total_amount}
Payment Status: {order.payment_status.title()}
Order Status: {order.order_status.replace('_', ' ').title()}

We will notify you again when your order is shipped.

Thank you for shopping with Veloura.
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        fail_silently=True,
    )


def send_order_shipped_email(order):
    if not order.email:
        return

    subject = f"Veloura Order Shipped - Order #{order.id}"
    message = f"""
Hello {order.full_name},

Good news — your order #{order.id} has been shipped.

Current Status: {order.order_status.replace('_', ' ').title()}

Estimated Delivery:
{order.estimated_delivery if order.estimated_delivery else 'Will be updated soon'}

Thank you for shopping with Veloura.
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        fail_silently=True,
    )


def send_cancel_approved_email(order_request):
    order = order_request.order
    if not order.email:
        return

    subject = f"Veloura Cancellation Approved - Order #{order.id}"
    message = f"""
Hello {order.full_name},

Your cancellation request for order #{order.id} has been approved.

Request Type: {order_request.get_request_type_display()}
Status: {order_request.get_status_display()}

Admin Note:
{order_request.admin_note or 'No additional note provided.'}

Thank you,
Veloura Support
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        fail_silently=True,
    )


def send_return_approved_email(order_request):
    order = order_request.order
    if not order.email:
        return

    subject = f"Veloura Return Approved - Order #{order.id}"
    message = f"""
Hello {order.full_name},

Your return request for order #{order.id} has been approved.

Request Type: {order_request.get_request_type_display()}
Status: {order_request.get_status_display()}

Admin Note:
{order_request.admin_note or 'No additional note provided.'}

Thank you,
Veloura Support
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        fail_silently=True,
    )


def test_email(request):
    send_mail(
        'Test Email from Veloura',
        'This is a test email.',
        settings.DEFAULT_FROM_EMAIL,
        ['yourtestemail@gmail.com'],
        fail_silently=False,
    )
    return HttpResponse("Test email sent")


def live_search(request):
    query = request.GET.get('q', '').strip()

    results = []

    if query:
        products = Product.objects.filter(
            name__icontains=query
        ) | Product.objects.filter(
            category__icontains=query
        ) | Product.objects.filter(
            description__icontains=query
        ) | Product.objects.filter(
            subcategory__icontains=query
        )

        for p in products[:6]:
            results.append({
                'id': p.id,
                'name': p.name,
                'price': str(p.price),
                'image': p.image.url if p.image else '',
            })

    return JsonResponse({'results': results})