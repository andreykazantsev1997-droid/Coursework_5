from tracker.apps import TrackerConfig
from django.urls import path
from rest_framework.routers import DefaultRouter
from tracker.views import TrackerViewSet, TrackerListAPIView

app_name = TrackerConfig.name

router = DefaultRouter()
router.register(r'trackers', TrackerViewSet, basename='trackers')

urlpatterns = [
    path('public/', TrackerListAPIView.as_view(), name='public-trackers'),
] + router.urls