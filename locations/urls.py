from django.urls import path
from .views import (
    LocationListView,
    LocationDetailView,
    LocationCreateView,
    LocationUpdateView,
    LocationDeleteView,
)

urlpatterns = [
    path('locations/', LocationListView.as_view(), name='location-list'),
    path('locations/create/', LocationCreateView.as_view(), name='location-create'),
    path('locations/<int:pk>/', LocationDetailView.as_view(), name='location-detail'),
    path('locations/<int:pk>/update/', LocationUpdateView.as_view(), name='location-update'),
    path('locations/<int:pk>/delete/', LocationDeleteView.as_view(), name='location-delete'),
]
