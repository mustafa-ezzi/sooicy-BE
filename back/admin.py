from django.contrib import admin
from .models import Rider, Location, Product, Order, OrderItem, OrderTracking

@admin.register(Rider)
class RiderAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'status', 'vehicle_type', 'rating', 'total_deliveries', 'is_active')
    list_filter = ('status', 'vehicle_type', 'is_active', 'created_at')
    search_fields = ('name', 'phone', 'email')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'area', 'delivery_fee', 'delivery_time', 'available')
    list_filter = ('available', 'created_at')
    search_fields = ('name', 'area', 'address')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discounted_price', 'is_available', 'rating')
    list_filter = ('category', 'is_available', 'created_at')
    search_fields = ('name', 'description', 'category')
    readonly_fields = ('discounted_price', 'created_at', 'updated_at')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('total_price',)

class OrderTrackingInline(admin.TabularInline):
    model = OrderTracking
    readonly_fields = ('timestamp',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'status', 'total', 'rider', 'created_at')
    list_filter = ('status', 'payment_method', 'delivery_type', 'created_at')
    search_fields = ('customer_name', 'customer_phone', 'customer_email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline, OrderTrackingInline]