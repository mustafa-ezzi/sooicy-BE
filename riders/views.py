from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Rider
from .serializers import RiderSerializer


#  GET all riders
class RiderListView(APIView):
    def get(self, request):
        riders = Rider.objects.all()
        serializer = RiderSerializer(riders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


#  GET rider by ID
class RiderDetailView(APIView):
    def get(self, request, pk):
        rider = get_object_or_404(Rider, pk=pk)
        serializer = RiderSerializer(rider)
        return Response(serializer.data, status=status.HTTP_200_OK)


#  POST create rider
class RiderCreateView(APIView):
    def post(self, request):
        serializer = RiderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#  PATCH update rider
class RiderUpdateView(APIView):
    def patch(self, request, pk):
        rider = get_object_or_404(Rider, pk=pk)
        serializer = RiderSerializer(rider, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#  DELETE rider
class RiderDeleteView(APIView):
    def delete(self, request, pk):
        rider = get_object_or_404(Rider, pk=pk)
        rider.delete()
        return Response({"message": "Rider deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

#  Update only rider status
class RiderStatusUpdateView(APIView):
    def patch(self, request, pk):
        rider = get_object_or_404(Rider, pk=pk)

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