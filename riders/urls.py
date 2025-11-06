from django.urls import path
from .views import (
    RiderListView,
    RiderDetailView,
    RiderCreateView,
    RiderStatusUpdateView,
    RiderUpdateView,
    RiderDeleteView,
)

urlpatterns = [
    path('riders/', RiderListView.as_view(), name='rider-list'),
    path('riders/create/', RiderCreateView.as_view(), name='rider-create'),
    path('riders/<int:pk>/', RiderDetailView.as_view(), name='rider-detail'),
    path('riders/<int:pk>/update/', RiderUpdateView.as_view(), name='rider-update'),
    path('riders/<int:pk>/delete/', RiderDeleteView.as_view(), name='rider-delete'),
    path('riders/<int:pk>/status/', RiderStatusUpdateView.as_view(), name='rider-status-update'),

]
