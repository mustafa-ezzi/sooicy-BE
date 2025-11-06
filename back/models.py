from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class SooicyUser(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    is_member = models.BooleanField(default=True)
    total_orders = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    join_date = models.DateTimeField(auto_now_add=True)
    last_order_date = models.DateTimeField(blank=True, null=True)
    favorite_items = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.email}"

    class Meta:
        ordering = ["-created_at"]


class Rider(models.Model):
    STATUS_CHOICES = [
        ("available", "Available"),
        ("busy", "Busy"),
        ("unavailable", "Unavailable"),
        ("offline", "Offline"),
    ]

    VEHICLE_CHOICES = [
        ("bike", "Bike"),
        ("scooter", "Scooter"),
        ("car", "Car"),
        ("bicycle", "Bicycle"),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    vehicle_type = models.CharField(
        max_length=20, choices=VEHICLE_CHOICES, default="bike"
    )
    license_number = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="available"
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=5.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
    )
    total_deliveries = models.IntegerField(default=0)
    current_orders = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"

    class Meta:
        ordering = ["-created_at"]


class Location(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    address = models.TextField()
    delivery_time = models.CharField(max_length=20)  # e.g., "15-25 min"
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    latitude = models.DecimalField(
        max_digits=10, decimal_places=8, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=11, decimal_places=8, blank=True, null=True
    )
    available = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    coverage_radius = models.IntegerField(default=5)  # in KM
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.area}"

    class Meta:
        ordering = ["name"]


class Addon(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - Rs {self.price}"

    class Meta:
        ordering = ["name"]


class Product(models.Model):
    CATEGORY_CHOICES = [
        ("scoop-whoop", "Scoop-Whoop"),
        ("swirls", "Swirls"),
        ("tera-mera", "Tera-Mera"),
        ("scoop & sip", "Scoop & Sip"),
        ("slay-sundae", "Slay-Sundae"),
        ("berry-berry", "Berry-Berry"),
        ("rizzler-shake", "Rizzler-Shake"),
        ("swirl`s-top", "Swirl`s-Top"),
        ("waffles", "Waffles"),
        ("sassy-pancakes", "Sassy-Pancakes"),
    ]
    is_popular = models.BooleanField(default=False)
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.URLField(blank=True, null=True)
    ingredients = models.JSONField(default=list, blank=True)
    preparation_time = models.CharField(max_length=20, blank=True, null=True)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=5.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
    )
    is_available = models.BooleanField(default=True)
    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
    )
    tags = models.JSONField(default=list, blank=True)
    addons = models.ManyToManyField("Addon", related_name="products", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def discounted_price(self):
        if self.discount > 0:
            return self.price * (1 - self.discount / 100)
        return self.price

    class Meta:
        ordering = ["-created_at"]


class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"


class Order(models.Model):
    sooicy_user = models.ForeignKey(
        "SooicyUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("preparing", "Preparing"),
        ("delivering", "Delivering"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_CHOICES = [
        ("card", "Credit/Debit Card"),
        ("cash", "Cash on Delivery"),
        ("digital", "Digital Wallet"),
    ]

    DELIVERY_TYPE_CHOICES = [
        ("delivery", "Delivery"),
        ("pickup", "Pickup"),
    ]

    id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15)
    customer_email = models.EmailField(blank=True, null=True)
    delivery_address = models.TextField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    delivery_type = models.CharField(
        max_length=20, choices=DELIVERY_TYPE_CHOICES, default="delivery"
    )
    pickup_location = models.CharField(max_length=100, blank=True, null=True)
    selected_location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, blank=True, null=True
    )
    rider = models.ForeignKey(Rider, on_delete=models.SET_NULL, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_time = models.CharField(max_length=20, blank=True, null=True)
    special_instructions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"

    class Meta:
        ordering = ["-created_at"]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    special_instructions = models.TextField(blank=True, null=True)
    addons = models.ManyToManyField('Addon', related_name='order_items', blank=True)
    addons_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calculate_total_price(self):
        """Calculate total item price including addons and quantity."""
        base_price = self.unit_price * self.quantity
        addon_total = self.addons_price * self.quantity
        return base_price + addon_total

    def save(self, *args, **kwargs):
        self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"


class OrderTracking(models.Model):
    order = models.ForeignKey(Order, related_name="tracking", on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    updated_by = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Order #{self.order.id} - {self.status}"

    class Meta:
        ordering = ["-timestamp"]
