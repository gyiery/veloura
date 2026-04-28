def cart_count(request):
    cart = request.session.get('cart', {})
    total_items = sum(item['quantity'] for item in cart.values())

    return {
        'cart_count': total_items
    }


def wishlist_count(request):
    wishlist = request.session.get('wishlist', {})
    return {
        'wishlist_count': len(wishlist)
    }