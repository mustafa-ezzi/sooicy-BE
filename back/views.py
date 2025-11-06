from rest_framework.views import APIView
from decimal import Decimal
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.files.storage import default_storage
from django.conf import settings
import os
from .models import Addon, Rider, Location, Product, Order, OrderItem, OrderTracking, SooicyUser
from .serializers import (
    AddonSerializer, RiderSerializer, LocationSerializer, ProductSerializer,
    OrderSerializer, OrderCreateSerializer, DashboardStatsSerializer,
    OrderTrackingSerializer
)

# ============ RIDER VIEWS ============

class RiderListView(APIView):
    def get(self, request):
        riders = Rider.objects.filter(is_active=True)
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            riders = riders.filter(status=status_filter)
            
        # Search functionality
        search = request.query_params.get('search')
        if search:
            riders = riders.filter(
                Q(name__icontains=search) | 
                Q(phone__icontains=search) |
                Q(email__icontains=search)
            )
            
        serializer = RiderSerializer(riders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RiderDetailView(APIView):
    def get(self, request, pk):
        rider = get_object_or_404(Rider, pk=pk, is_active=True)
        serializer = RiderSerializer(rider)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RiderCreateView(APIView):
    def post(self, request):
        serializer = RiderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RiderUpdateView(APIView):
    def patch(self, request, pk):
        rider = get_object_or_404(Rider, pk=pk, is_active=True)
        serializer = RiderSerializer(rider, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RiderDeleteView(APIView):
    def delete(self, request, pk):
        rider = get_object_or_404(Rider, pk=pk, is_active=True)
        rider.is_active = False  # Soft delete
        rider.save()
        return Response({"message": "Rider deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class RiderStatusUpdateView(APIView):
    def patch(self, request, pk):
        rider = get_object_or_404(Rider, pk=pk, is_active=True)
        
        new_status = request.data.get("status")
        if new_status not in dict(Rider.STATUS_CHOICES).keys():
            return Response(
                {"error": f"Invalid status. Allowed: {list(dict(Rider.STATUS_CHOICES).keys())}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rider.status = new_status
        rider.save()
        
        serializer = RiderSerializer(rider)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ============ LOCATION VIEWS ============

class LocationListView(APIView):
    def get(self, request):
        locations = Location.objects.all()
        
        # Filter by availability
        available_filter = request.query_params.get('available')
        if available_filter is not None:
            available = available_filter.lower() == 'true'
            locations = locations.filter(available=available)
            
        # Search functionality
        search = request.query_params.get('search')
        if search:
            locations = locations.filter(
                Q(name__icontains=search) |
                Q(area__icontains=search) |
                Q(address__icontains=search)
            )
            
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LocationDetailView(APIView):
    def get(self, request, pk):
        location = get_object_or_404(Location, pk=pk)
        serializer = LocationSerializer(location)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LocationCreateView(APIView):
    def post(self, request):
        serializer = LocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LocationUpdateView(APIView):
    def patch(self, request, pk):
        location = get_object_or_404(Location, pk=pk)
        serializer = LocationSerializer(location, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LocationDeleteView(APIView):
    def delete(self, request, pk):
        location = get_object_or_404(Location, pk=pk)
        location.delete()
        return Response({"message": "Location deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class LocationToggleAvailabilityView(APIView):
    def patch(self, request, pk):
        location = get_object_or_404(Location, pk=pk)
        location.available = not location.available
        location.save()
        
        serializer = LocationSerializer(location)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ============ PRODUCT VIEWS ============

class ProductListView(APIView):
    def get(self, request):
        products = Product.objects.all()
        
        # Filter by category
        category_filter = request.query_params.get('category')
        if category_filter:
            products = products.filter(category=category_filter)
            
        # Filter by availability
        available_filter = request.query_params.get('available')
        if available_filter is not None:
            available = available_filter.lower() == 'true'
            products = products.filter(is_available=available)
            
        # Search functionality
        search = request.query_params.get('search')
        if search:
            products = products.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(category__icontains=search)
            )
            
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProductDetailView(APIView):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProductCreateView(APIView):
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductUpdateView(APIView):
    def patch(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDeleteView(APIView):
    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class ProductImageUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        image = request.FILES.get('image')
        if not image:
            return Response(
                {"error": "No image file provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file size (max 5MB)
        if image.size > 5 * 1024 * 1024:
            return Response(
                {"error": "File size too large. Maximum 5MB allowed."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if image.content_type not in allowed_types:
            return Response(
                {"error": "Invalid file type. Only JPEG, PNG, GIF, and WebP are allowed."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Save file
            filename = f"products/{timezone.now().strftime('%Y%m%d_%H%M%S')}_{image.name}"
            filepath = default_storage.save(filename, image)
            image_url = default_storage.url(filepath)
            
            return Response(
                {"imageUrl": image_url}, 
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to upload image: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class ProductCategoryListView(APIView):
    """
    Returns the list of available product categories from Product.CATEGORY_CHOICES
    """
    def get(self, request):
        return Response(Product.CATEGORY_CHOICES, status=status.HTTP_200_OK)

# ============ ADDONS ==============
class AddonListView(APIView):
    def get(self, request):
        addons = Addon.objects.all()

        # Filter by availability
        available_filter = request.query_params.get('available')
        if available_filter is not None:
            available = available_filter.lower() == 'true'
            addons = addons.filter(is_available=available)

        # Search by name or description
        search = request.query_params.get('search')
        if search:
            addons = addons.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )

        serializer = AddonSerializer(addons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ✅ GET single addon by ID
class AddonDetailView(APIView):
    def get(self, request, pk):
        addon = get_object_or_404(Addon, pk=pk)
        serializer = AddonSerializer(addon)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ✅ POST create new addon
class AddonCreateView(APIView):
    def post(self, request):
        serializer = AddonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ PATCH update addon
class AddonUpdateView(APIView):
    def patch(self, request, pk):
        addon = get_object_or_404(Addon, pk=pk)
        serializer = AddonSerializer(addon, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ DELETE addon
class AddonDeleteView(APIView):
    def delete(self, request, pk):
        addon = get_object_or_404(Addon, pk=pk)
        addon.delete()
        return Response(
            {"message": "Addon deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


# ============ ORDER VIEWS ============

class OrderListView(APIView):
    def get(self, request):
        orders = Order.objects.all().select_related('rider', 'selected_location').prefetch_related('items__product')
        
        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            orders = orders.filter(status=status_filter)
            
        # Filter by date range
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        if date_from:
            orders = orders.filter(created_at__date__gte=date_from)
        if date_to:
            orders = orders.filter(created_at__date__lte=date_to)
            
        # Search functionality
        search = request.query_params.get('search')
        if search:
            orders = orders.filter(
                Q(id__icontains=search) |
                Q(customer_name__icontains=search) |
                Q(customer_phone__icontains=search)
            )
            
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class OrderDetailView(APIView):
    def get(self, request, pk):
        order = get_object_or_404(
            Order.objects.select_related('rider', 'selected_location').prefetch_related('items__product', 'tracking'), 
            pk=pk
        )
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

class OrderCreateView(APIView):
    def post(self, request):
        print("=" * 80)
        print("INCOMING REQUEST DATA:")
        print(request.data)
        print("=" * 80)
        
        sooicy_user_id = request.data.get('sooicy_user')
        sooicy_user_instance = None

        if sooicy_user_id:
            try:
                sooicy_user_instance = SooicyUser.objects.get(id=sooicy_user_id)
            except SooicyUser.DoesNotExist:
                return Response(
                    {"error": f"SooicyUser with id {sooicy_user_id} does not exist"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # ✅ Extract items_data FIRST before making a copy
        items_data = request.data.get('items_data', [])
        
        # Validate items_data is not empty
        if not items_data or len(items_data) == 0:
            return Response(
                {"error": "items_data is required and cannot be empty"},
                status=status.HTTP_400_BAD_REQUEST
            )

        print(f"Extracted items_data: {items_data}")

        # ✅ Now create order_data INCLUDING items_data for serializer validation
        order_data = {
            'customer_name': request.data.get('customer_name'),
            'customer_phone': request.data.get('customer_phone'),
            'customer_email': request.data.get('customer_email'),
            'delivery_address': request.data.get('delivery_address'),
            'payment_method': request.data.get('payment_method'),
            'delivery_type': request.data.get('delivery_type'),
            'pickup_location': request.data.get('pickup_location'),
            'selected_location': request.data.get('selected_location'),
            'subtotal': request.data.get('subtotal'),
            'delivery_fee': request.data.get('delivery_fee'),
            'tax': request.data.get('tax'),
            'total': request.data.get('total'),
            'estimated_time': request.data.get('estimated_time'),
            'special_instructions': request.data.get('special_instructions', ''),
            'items_data': items_data,  # ✅ Include items_data for serializer
        }

        print(f"Order data for serializer: {order_data}")

        serializer = OrderCreateSerializer(data=order_data)
        if not serializer.is_valid():
            print(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = serializer.save()
            if sooicy_user_instance:
                order.sooicy_user = sooicy_user_instance
                order.save()

            print(f"Order created: #{order.id}")

            total_amount = Decimal('0.00')

            # Process items from items_data
            for item_data in items_data:
                product_id = item_data.get('product_id')
                if not product_id:
                    print("Skipping item - no product_id")
                    continue
                    
                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    print(f"Product {product_id} not found")
                    continue
                
                quantity = int(item_data.get('quantity', 1))
                unit_price = Decimal(str(product.price))

                print(f"\nProcessing item: {product.name}")
                print(f"Quantity: {quantity}, Unit Price: {unit_price}")

                # Create the order item
                order_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    special_instructions=item_data.get('special_instructions', '')
                )

                # Process addons
                selected_addons = item_data.get('selectedAddons', [])
                print(f"Selected addons: {selected_addons}")

                if selected_addons and len(selected_addons) > 0:
                    addon_ids = []
                    for addon_data in selected_addons:
                        addon_id = addon_data.get('id')
                        if addon_id:
                            addon_ids.append(int(addon_id))
                    
                    print(f"Addon IDs to fetch: {addon_ids}")
                    
                    if addon_ids:
                        addons = Addon.objects.filter(id__in=addon_ids)
                        print(f"Found addons: {list(addons.values_list('id', 'name', 'price'))}")
                        
                        order_item.addons.set(addons)
                        
                        # Calculate total addon price
                        addons_total = sum((addon.price for addon in addons), Decimal('0.00'))
                        order_item.addons_price = addons_total
                        
                        print(f"Addons total price: {addons_total}")
                        
                        # Save to recalculate total_price
                        order_item.save()

                # Refresh from DB to get updated total_price
                order_item.refresh_from_db()
                
                print(f"Order item total_price (with addons): {order_item.total_price}")
                
                # Add to order total
                total_amount += order_item.total_price
                print(f"Running order total: {total_amount}")

            # Update order totals
            print(f"\n{'='*50}")
            print("CALCULATING ORDER TOTALS")
            print(f"{'='*50}")
            
            order.subtotal = total_amount
            order.tax = total_amount * Decimal('0.08')
            
            if order.delivery_type == 'delivery' and order.selected_location:
                order.delivery_fee = order.selected_location.delivery_fee
            else:
                order.delivery_fee = Decimal('0.00')
            
            order.total = order.subtotal + order.tax + order.delivery_fee
            
            print(f"Subtotal (from items): {order.subtotal}")
            print(f"Tax (8%): {order.tax}")
            print(f"Delivery Fee: {order.delivery_fee}")
            print(f"FINAL TOTAL: {order.total}")
            print(f"{'='*50}\n")
            
            order.save()

            # Update user stats
            if sooicy_user_instance:
                sooicy_user_instance.total_orders += 1
                sooicy_user_instance.total_spent += order.total
                sooicy_user_instance.last_order_date = timezone.now()
                sooicy_user_instance.save()
                print(f"Updated user stats: {sooicy_user_instance.name}")

            # Set estimated delivery time
            if order.delivery_type == 'pickup':
                order.estimated_time = '15-20 minutes'
            else:
                base_time = 25
                location_adjustment = getattr(order.selected_location, 'delivery_time_minutes', 10) if order.selected_location else 10
                total_time = base_time + location_adjustment
                order.estimated_time = f'{total_time}-{total_time + 10} minutes'
            order.save()

            # Create tracking entry
            OrderTracking.objects.create(
                order=order,
                status='pending',
                notes=f"Order #{order.id} created successfully",
                updated_by='System'
            )

            print(f"\n✅ ORDER CREATED SUCCESSFULLY: #{order.id}")
            print(f"Total with addons: {order.total}")
            print("=" * 80 + "\n")

            order_serializer = OrderSerializer(order)
            return Response({
                **order_serializer.data,
                'message': 'Order created successfully',
                'estimated_time': order.estimated_time
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"\n❌ ERROR CREATING ORDER: {str(e)}")
            import traceback
            traceback.print_exc()
            
            if 'order' in locals():
                order.delete()
                print("Rolled back order creation")
            
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class OrderStatusUpdateView(APIView):
    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        
        new_status = request.data.get("status")
        if new_status not in dict(Order.STATUS_CHOICES).keys():
            return Response(
                {"error": f"Invalid status. Allowed: {list(dict(Order.STATUS_CHOICES).keys())}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = order.status
        order.status = new_status
        order.save()
        
        # Create tracking entry
        OrderTracking.objects.create(
            order=order,
            status=new_status,
            notes=f"Status changed from {old_status} to {new_status}",
            updated_by=request.data.get('updated_by', 'System')
        )
        
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

class OrderAssignRiderView(APIView):
    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        rider_id = request.data.get('rider_id')
        
        if not rider_id:
            return Response(
                {"error": "Rider ID is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rider = get_object_or_404(Rider, pk=rider_id, is_active=True)
        
        if rider.status != 'available':
            return Response(
                {"error": "Rider is not available"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update order
        order.rider = rider
        if order.status == 'pending':
            order.status = 'preparing'
        order.save()
        
        # Update rider
        rider.current_orders += 1
        if rider.current_orders >= 3:  # Max concurrent orders
            rider.status = 'busy'
        rider.save()
        
        # Create tracking entry
        OrderTracking.objects.create(
            order=order,
            status='assigned',
            notes=f"Order assigned to rider {rider.name}",
            updated_by=request.data.get('updated_by', 'System')
        )
        
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ============User Orders ============
class UserCreateOrGetView(APIView):
    def post(self, request):
        email = request.data.get('email')
        name = request.data.get('name')
        phone = request.data.get('phone')
        address = request.data.get('address', '')

        if not email or not name or not phone:
            return Response(
                {"error": "Email, name, and phone are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user already exists
        try:
            user = SooicyUser.objects.get(email=email)
            is_new_user = False
            
            # Update user info if provided
            if name != user.name:
                user.name = name
            if phone != user.phone:
                user.phone = phone
            if address and address != user.address:
                user.address = address
            user.save()
            
        except SooicyUser.DoesNotExist:
            # Create new user
            user = SooicyUser.objects.create(
                name=name,
                email=email,
                phone=phone,
                address=address,
                is_member=True
            )
            is_new_user = True

        return Response({
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'address': user.address,
                'is_member': user.is_member,
                'total_orders': user.total_orders,
                'total_spent': float(user.total_spent),
                'join_date': user.join_date,
                'last_order_date': user.last_order_date,
            },
            'is_new_user': is_new_user,
            'message': 'Welcome to the Sooicy family!' if is_new_user else f'Welcome back, {user.name}!'
        }, status=status.HTTP_200_OK)

class UserOrdersView(APIView):
    def get(self, request, user_id):
        try:
            user = SooicyUser.objects.get(id=user_id)
        except SooicyUser.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get orders for this user
        orders = Order.objects.filter(
            sooicy_user=user
        ).select_related('rider', 'selected_location').prefetch_related('items__product')
        
        # Apply filters like in your existing OrderListView
        status_filter = request.query_params.get('status')
        if status_filter:
            orders = orders.filter(status=status_filter)
            
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        if date_from:
            orders = orders.filter(created_at__date__gte=date_from)
        if date_to:
            orders = orders.filter(created_at__date__lte=date_to)
            
        search = request.query_params.get('search')
        if search:
            orders = orders.filter(
                Q(id__icontains=search) |
                Q(customer_name__icontains=search) |
                Q(customer_phone__icontains=search)
            )
            
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



# ============ DASHBOARD VIEWS ============

class DashboardStatsView(APIView):
    def get(self, request):
        # Calculate date ranges
        today = timezone.now().date()
        
        # Order statistics
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        delivering_orders = Order.objects.filter(status='delivering').count()
        completed_orders = Order.objects.filter(status='delivered').count()
        cancelled_orders = Order.objects.filter(status='cancelled').count()
        orders_today = Order.objects.filter(created_at__date=today).count()
        
        # Revenue statistics
        total_revenue = Order.objects.filter(status='delivered').aggregate(
            total=Sum('total')
        )['total'] or 0
        
        revenue_today = Order.objects.filter(
            created_at__date=today, 
            status='delivered'
        ).aggregate(total=Sum('total'))['total'] or 0
        
        # Rider statistics
        total_riders = Rider.objects.filter(is_active=True).count()
        available_riders = Rider.objects.filter(status='available', is_active=True).count()
        
        # Product and location statistics
        total_products = Product.objects.count()
        total_locations = Location.objects.count()
        
        stats_data = {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'delivering_orders': delivering_orders,
            'completed_orders': completed_orders,
            'cancelled_orders': cancelled_orders,
            'orders_today': orders_today,
            'total_revenue': total_revenue,
            'revenue_today': revenue_today,
            'total_riders': total_riders,
            'available_riders': available_riders,
            'total_products': total_products,
            'total_locations': total_locations,
            }
        
        serializer = DashboardStatsSerializer(stats_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RecentOrdersView(APIView):
    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        orders = Order.objects.select_related('rider', 'selected_location').prefetch_related('items__product')[:limit]
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class OrderTrackingView(APIView):
    def get(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        tracking = OrderTracking.objects.filter(order=order)
        serializer = OrderTrackingSerializer(tracking, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ============ ANALYTICS VIEWS ============

class SalesAnalyticsView(APIView):
    def get(self, request):
        # Get date range from query params
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Daily sales data
        daily_sales = []
        current_date = start_date
        while current_date <= end_date:
            day_orders = Order.objects.filter(
                created_at__date=current_date,
                status='delivered'
            )
            daily_revenue = day_orders.aggregate(total=Sum('total'))['total'] or 0
            daily_sales.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'revenue': float(daily_revenue),
                'orders': day_orders.count()
            })
            current_date += timedelta(days=1)
        
        # Top products
        top_products = Product.objects.annotate(
            order_count=Count('orderitem__order', filter=Q(orderitem__order__status='delivered'))
        ).order_by('-order_count')[:5]
        
        top_products_data = [{
            'id': product.id,
            'name': product.name,
            'orders': product.order_count,
            'revenue': float(OrderItem.objects.filter(
                product=product,
                order__status='delivered'
            ).aggregate(total=Sum('total_price'))['total'] or 0)
        } for product in top_products]
        
        # Category performance
        category_stats = {}
        for choice in Product.CATEGORY_CHOICES:
            category = choice[0]
            revenue = OrderItem.objects.filter(
                product__category=category,
                order__status='delivered'
            ).aggregate(total=Sum('total_price'))['total'] or 0
            
            category_stats[choice[1]] = float(revenue)
        
        return Response({
            'daily_sales': daily_sales,
            'top_products': top_products_data,
            'category_performance': category_stats,
            'date_range': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d')
            }
        }, status=status.HTTP_200_OK)

# ============ UTILITY VIEWS ============

class CategoryListView(APIView):
    def get(self, request):
        categories = [{'value': choice[0], 'label': choice[1]} for choice in Product.CATEGORY_CHOICES]
        return Response(categories, status=status.HTTP_200_OK)

class StatusChoicesView(APIView):
    def get(self, request):
        model = request.query_params.get('model')
        
        if model == 'rider':
            choices = [{'value': choice[0], 'label': choice[1]} for choice in Rider.STATUS_CHOICES]
        elif model == 'order':
            choices = [{'value': choice[0], 'label': choice[1]} for choice in Order.STATUS_CHOICES]
        elif model == 'vehicle':
            choices = [{'value': choice[0], 'label': choice[1]} for choice in Rider.VEHICLE_CHOICES]
        elif model == 'payment':
            choices = [{'value': choice[0], 'label': choice[1]} for choice in Order.PAYMENT_CHOICES]
        else:
            return Response(
                {"error": "Invalid model. Available: rider, order, vehicle, payment"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(choices, status=status.HTTP_200_OK)

# ============ BULK OPERATIONS ============

class BulkRiderStatusUpdateView(APIView):
    def patch(self, request):
        rider_ids = request.data.get('rider_ids', [])
        new_status = request.data.get('status')
        
        if not rider_ids:
            return Response(
                {"error": "No rider IDs provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_status not in dict(Rider.STATUS_CHOICES).keys():
            return Response(
                {"error": f"Invalid status. Allowed: {list(dict(Rider.STATUS_CHOICES).keys())}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated_count = Rider.objects.filter(
            id__in=rider_ids, 
            is_active=True
        ).update(status=new_status)
        
        return Response({
            "message": f"Updated {updated_count} riders to {new_status} status"
        }, status=status.HTTP_200_OK)

class BulkProductUpdateView(APIView):
    def patch(self, request):
        product_ids = request.data.get('product_ids', [])
        updates = request.data.get('updates', {})
        
        if not product_ids:
            return Response(
                {"error": "No product IDs provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate updates
        allowed_fields = ['is_available', 'discount', 'category']
        invalid_fields = set(updates.keys()) - set(allowed_fields)
        if invalid_fields:
            return Response(
                {"error": f"Invalid fields: {list(invalid_fields)}. Allowed: {allowed_fields}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated_count = Product.objects.filter(id__in=product_ids).update(**updates)
        
        return Response({
            "message": f"Updated {updated_count} products"
        }, status=status.HTTP_200_OK)