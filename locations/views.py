from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Location
from .serializers import LocationSerializer


#  GET all locations
class LocationListView(APIView):
    def get(self, request):
        locations = Location.objects.all()
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


#  GET location by ID
class LocationDetailView(APIView):
    def get(self, request, pk):
        location = get_object_or_404(Location, pk=pk)
        serializer = LocationSerializer(location)
        return Response(serializer.data, status=status.HTTP_200_OK)


#  POST create location
class LocationCreateView(APIView):
    def post(self, request):
        serializer = LocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#  PATCH update location
class LocationUpdateView(APIView):
    def patch(self, request, pk):
        location = get_object_or_404(Location, pk=pk)
        serializer = LocationSerializer(location, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#  DELETE location
class LocationDeleteView(APIView):
    def delete(self, request, pk):
        location = get_object_or_404(Location, pk=pk)
        location.delete()
        return Response({"message": "Location deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
