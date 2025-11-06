from django.urls import path
from . import views

urlpatterns = [
    # ============ RIDER URLS ============
    path('riders/', views.RiderListView.as_view(), name='rider-list'),
    path('riders/<int:pk>/', views.RiderDetailView.as_view(), name='rider-detail'),
    path('riders/create/', views.RiderCreateView.as_view(), name='rider-create'),
    path('riders/<int:pk>/update/', views.RiderUpdateView.as_view(), name='rider-update'),
    path('riders/<int:pk>/delete/', views.RiderDeleteView.as_view(), name='rider-delete'),
    path('riders/<int:pk>/status/', views.RiderStatusUpdateView.as_view(), name='rider-status-update'),
    path('riders/bulk-status/', views.BulkRiderStatusUpdateView.as_view(), name='bulk-rider-status'),
    
    # ============ LOCATION URLS ============
    path('locations/', views.LocationListView.as_view(), name='location-list'),
    path('locations/<int:pk>/', views.LocationDetailView.as_view(), name='location-detail'),
    path('locations/create/', views.LocationCreateView.as_view(), name='location-create'),
    path('locations/<int:pk>/update/', views.LocationUpdateView.as_view(), name='location-update'),
    path('locations/<int:pk>/delete/', views.LocationDeleteView.as_view(), name='location-delete'),
    path('locations/<int:pk>/toggle-availability/', views.LocationToggleAvailabilityView.as_view(), name='location-toggle'),
    
    # ============ PRODUCT URLS ============
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('products/create/', views.ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),
    path('products/upload-image/', views.ProductImageUploadView.as_view(), name='product-image-upload'),
    path('products/bulk-update/', views.BulkProductUpdateView.as_view(), name='bulk-product-update'),
        path('products/categories/', views.ProductCategoryListView.as_view(), name='product-categories'),  # ✅ new endpoint

    # =========== ADDON URLS ============
    path('addons/', views.AddonListView.as_view(), name='addon-list'),
    path('addons/create/', views.AddonCreateView.as_view(), name='addon-create'),
    path('addons/<int:pk>/', views.AddonDetailView.as_view(), name='addon-detail'),
    path('addons/<int:pk>/update/', views.AddonUpdateView.as_view(), name='addon-update'),
    path('addons/<int:pk>/delete/', views.AddonDeleteView.as_view(), name='addon-delete'),
   
   
    # ============ ORDER URLS ============
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/create/', views.OrderCreateView.as_view(), name='order-create'),
    path('orders/<int:pk>/status/', views.OrderStatusUpdateView.as_view(), name='order-status-update'),
    path('orders/<int:pk>/assign-rider/', views.OrderAssignRiderView.as_view(), name='order-assign-rider'),
    path('orders/<int:order_id>/tracking/', views.OrderTrackingView.as_view(), name='order-tracking'),
    path('orders/recent/', views.RecentOrdersView.as_view(), name='recent-orders'),
    path('user/create-or-get/', views.UserCreateOrGetView.as_view(), name='user-create-or-get'),
    path('user/<int:user_id>/orders/', views.UserOrdersView.as_view(), name='user-orders'),
    
    # ============ DASHBOARD URLS ============
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard/analytics/', views.SalesAnalyticsView.as_view(), name='sales-analytics'),
    
    # ============ UTILITY URLS ============
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('status-choices/', views.StatusChoicesView.as_view(), name='status-choices'),
]