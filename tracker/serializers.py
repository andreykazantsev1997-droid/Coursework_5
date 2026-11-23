from rest_framework import serializers

from tracker.models import Tracker
from tracker.validators import (
    TrackerValidator,
    RangeValidator,
    PleasantValidator,
    PleasantTrackValidator,
    PeriodicityValidator,
)


class TrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tracker
        fields = "__all__"
        read_only_fields = ("user",)
        validators = [
            TrackerValidator(reward="reward", tracker_stacking="tracker_stacking"),
            RangeValidator(completion_time="completion_time"),
            PleasantValidator(tracker_stacking="tracker_stacking"),
            PleasantTrackValidator(
                pleasant_tracker="pleasant_tracker", reward="reward", tracker_stacking="tracker_stacking"
            ),
            PeriodicityValidator(periodicity="periodicity"),
        ]
