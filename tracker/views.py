from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from tracker.models import Tracker
from tracker.paginators import CustomPaginator
from tracker.permissions import IsOwner
from tracker.serializers import TrackerSerializer

# Create your views here.
class TrackerViewSet(ModelViewSet):
    serializer_class = TrackerSerializer
    pagination_class = CustomPaginator
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Tracker.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TrackerListAPIView(ListAPIView):
    serializer_class = TrackerSerializer
    pagination_class = CustomPaginator
    permission_classes = [IsAuthenticated]
    queryset = Tracker.objects.filter(publicness=True)

