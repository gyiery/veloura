from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Women', 'Women'),
        ('Men', 'Men'),
        ('Kids', 'Kids'),
        ('Home', 'Accessories'),
        ('Perfume', 'Perfume'),
    ]

    GENDER_CHOICES = [
        ('Men', 'Men'),
        ('Women', 'Women'),
    ]

    ACCESSORY_TYPE_CHOICES = [
        ('Shoes', 'Shoes'),
        ('Watches', 'Watches'),
        ('Glasses', 'Glasses'),
        ('Belts', 'Belts'),
        ('Wallets', 'Wallets'),
        ('Purse', 'Purse'),
        ('Jewellery', 'Jewellery'),
        ('Skin-Care', 'Skin-Care'),
    ]

    SUBCATEGORY_CHOICES = [
        ('Shirts', 'Shirts'),
        ('T-Shirts', 'T-Shirts'),
        ('Jeans', 'Jeans'),
        ('Formal', 'Formal'),
        ('Polos', 'Polos'),
        ('Jackets', 'Jackets'),
        ('Trousers', 'Trousers'),
        ('Dresses', 'Dresses'),
        ('Tops', 'Tops'),
        ('Kurtas', 'Kurtas'),
        ('Sarees', 'Sarees'),
        ('Skirts', 'Skirts'),
        ('Co-ords', 'Co-ords'),
        ('Leggings', 'Leggings'),
        ('Boys Wear', 'Boys Wear'),
        ('Girls Wear', 'Girls Wear'),
        ('Sets', 'Sets'),
        ('Nightwear', 'Nightwear'),
        ('Baby Wear', 'Baby Wear'),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Women')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    description = models.TextField()
    is_new_arrival = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)

    is_on_sale = models.BooleanField(default=False)
    sale_percent = models.PositiveIntegerField(default=0)

    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)
    accessory_type = models.CharField(max_length=50, choices=ACCESSORY_TYPE_CHOICES, blank=True, null=True)
    subcategory = models.CharField(max_length=50, choices=SUBCATEGORY_CHOICES, blank=True, null=True)

    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def stock_status(self):
        if self.stock <= 0:
            return "Out of Stock"
        if self.stock <= 5:
            return "Low Stock"
        return "In Stock"
        
@property
def sale_price(self):
    if self.is_on_sale and self.sale_percent > 0:
        discount = (self.price * self.sale_percent) / 100
        return self.price - discount
    return self.price

@property
def has_valid_sale(self):
    return self.is_on_sale and self.sale_percent > 0


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True, null=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f"{self.product.name} Image {self.id}"
    


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} - {self.user.username} - {self.rating}"


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return self.user.username


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='India')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def full_address(self):
        parts = [
            self.address_line_1,
            self.address_line_2,
            self.city,
            self.state,
            self.postal_code,
            self.country,
        ]
        return ", ".join([part for part in parts if part])

    def __str__(self):
        return f"{self.full_name} - {self.city}"


class Order(models.Model):
    PAYMENT_PROVIDER_CHOICES = [
        ('razorpay', 'Razorpay'),
        ('stripe', 'Stripe'),
        ('cod', 'Cash on Delivery'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('created', 'Created'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    ORDER_STATUS_CHOICES = [
    ('placed', 'Placed'),
    ('packed', 'Packed'),
    ('shipped', 'Shipped'),
    ('out_for_delivery', 'Out for Delivery'),
    ('delivered', 'Delivered'),
    ]

    order_status = models.CharField(
    max_length=30,
    choices=ORDER_STATUS_CHOICES,
    default='placed'
)

    estimated_delivery = models.DateField(blank=True, null=True)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    full_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_provider = models.CharField(max_length=20, choices=PAYMENT_PROVIDER_CHOICES, default='razorpay')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')

    gateway_order_id = models.CharField(max_length=255, blank=True, null=True)
    gateway_payment_id = models.CharField(max_length=255, blank=True, null=True)
    gateway_signature = models.CharField(max_length=500, blank=True, null=True)
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)

    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.full_name} - {self.payment_status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    image = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.product_name

class OrderRequest(models.Model):
    REQUEST_TYPE_CHOICES = [
        ('cancel', 'Cancel'),
        ('return', 'Return'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.order.id} - {self.request_type} - {self.status}"



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    UserProfile.objects.get_or_create(user=instance)



class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('flat', 'Flat'),
        ('percent', 'Percent'),
    ]

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code.upper()
    
class SupportTicket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    admin_reply = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.subject}"
    
class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email
    
class ReturnOrder(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    reason = models.TextField()
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Return request for Order #{self.order.id}"