from rest_framework import serializers
from .models import (
    Addon,
    Rider,
    Location,
    Product,
    Order,
    OrderItem,
    OrderTracking,
    Customer,
    SooicyUser,
)


class RiderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rider
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_phone(self, value):
        # Remove any existing rider with same phone (for updates)
        if self.instance:
            if Rider.objects.exclude(pk=self.instance.pk).filter(phone=value).exists():
                raise serializers.ValidationError(
                    "A rider with this phone number already exists."
                )
        else:
            if Rider.objects.filter(phone=value).exists():
                raise serializers.ValidationError(
                    "A rider with this phone number already exists."
                )
        return value


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_delivery_fee(self, value):
        if value < 0:
            raise serializers.ValidationError("Delivery fee cannot be negative.")
        return value

    def validate_coverage_radius(self, value):
        if value <= 0:
            raise serializers.ValidationError("Coverage radius must be greater than 0.")
        return value


class AddonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Addon
        fields = ["id", "name", "price", "description", "is_available"]


class ProductSerializer(serializers.ModelSerializer):
    discounted_price = serializers.ReadOnlyField()
    addons = AddonSerializer(many=True, read_only=True)
    addon_ids = serializers.PrimaryKeyRelatedField(
        queryset=Addon.objects.all(), many=True, write_only=True, required=False
    )

    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "discounted_price")

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value

    def validate_discount(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Discount must be between 0 and 100 percent."
            )
        return value

    def create(self, validated_data):
        addon_ids = validated_data.pop("addon_ids", [])
        product = Product.objects.create(**validated_data)
        if addon_ids:
            product.addons.set(addon_ids)
        return product

    def update(self, instance, validated_data):
        addon_ids = validated_data.pop("addon_ids", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if addon_ids is not None:
            instance.addons.set(addon_ids)
        return instance


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_image = serializers.URLField(source="product.image", read_only=True)
    addons_detail = AddonSerializer(source="addons", many=True, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product_name",
            "product_image",
            "quantity",
            "unit_price",
            "total_price",
            "special_instructions",
            "addons_price",
            "order",
            "product",
            "addons_detail",
        ]
        read_only_fields = ("id", "total_price")


class OrderTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTracking
        fields = "__all__"
        read_only_fields = ("id", "timestamp")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    tracking = OrderTrackingSerializer(many=True, read_only=True)
    rider_name = serializers.CharField(source="rider.name", read_only=True)
    rider = RiderSerializer(read_only=True)  # ✅ full nested rider details

    location_name = serializers.CharField(
        source="selected_location.name", read_only=True
    )

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_total(self, value):
        if value <= 0:
            raise serializers.ValidationError("Total must be greater than 0.")
        return value


class OrderCreateSerializer(serializers.ModelSerializer):
    items_data = serializers.ListField(write_only=True)
    sooicy_user = serializers.IntegerField(
        required=False, allow_null=True, write_only=True
    )

    class Meta:
        model = Order
        fields = [
            "customer_name",
            "customer_phone",
            "customer_email",
            "delivery_address",
            "payment_method",
            "delivery_type",
            "pickup_location",
            "selected_location",
            "subtotal",
            "delivery_fee",
            "tax",
            "total",
            "special_instructions",
            "items_data",
            "sooicy_user",
        ]

    def create(self, validated_data):
        # Remove items_data and sooicy_user from validated_data
        # We'll handle these manually in the view
        validated_data.pop("items_data", None)
        validated_data.pop("sooicy_user", None)

        # Create order without items (we'll add them in the view with addons)
        order = Order.objects.create(**validated_data)
        return order


# Dashboard Statistics Serializer
class DashboardStatsSerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    delivering_orders = serializers.IntegerField()
    completed_orders = serializers.IntegerField()
    cancelled_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_riders = serializers.IntegerField()
    available_riders = serializers.IntegerField()
    total_products = serializers.IntegerField()
    total_locations = serializers.IntegerField()
    orders_today = serializers.IntegerField()
    revenue_today = serializers.DecimalField(max_digits=15, decimal_places=2)


class SooicyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SooicyUser
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "address",
            "is_member",
            "total_orders",
            "total_spent",
            "join_date",
            "last_order_date",
        ]
