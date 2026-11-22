from rest_framework.serializers import ValidationError

class TrackerValidator:
    def __init__(self, reward: str, tracker_stacking: str):
        self.reward = reward
        self.tracker_stacking = tracker_stacking

    def __call__(self, attrs: dict):
        first_val = attrs.get(self.reward)
        second_val = attrs.get(self.tracker_stacking)
        reward_text = first_val.strip() if isinstance(first_val, str) else None
        if reward_text and second_val is not None:
            raise ValidationError("Нельзя одновременно указывать награду и связанную привычку")


class RangeValidator:
    def __init__(self, completion_time: str):
        self.completion_time = completion_time
        self.min_value = 1
        self.max_value = 120

    def __call__(self, attrs: dict):
        value = attrs.get(self.completion_time)
        if value is not None and isinstance(value, (int, float)) and not isinstance(value, bool) and not (self.min_value <= value <= self.max_value):
            raise ValidationError("Время выполнения должно быть от 1 до 120 секунд")


class PleasantValidator:
    def __init__(self, tracker_stacking: str):
        self.tracker_stacking = tracker_stacking

    def __call__(self, attrs: dict):
        linked_tracker = attrs.get(self.tracker_stacking)
        if linked_tracker is None:
            return
        is_pleasant = getattr(linked_tracker, "pleasant_tracker", False)
        if is_pleasant is not True:
            raise ValidationError("В связанные привычки можно добавлять только приятные привычки")


class PleasantTrackValidator:
    def __init__(self, pleasant_tracker: str, reward: str, tracker_stacking: str):
        self.pleasant_tracker = pleasant_tracker
        self.reward = reward
        self.tracker_stacking = tracker_stacking

    def __call__(self, attrs: dict):
        is_pleasant = attrs.get(self.pleasant_tracker)
        if is_pleasant is not True:
            return

        reward = attrs.get(self.reward)
        tracker_stacking = attrs.get(self.tracker_stacking)

        has_reward = (
            reward is not None
            and not isinstance(reward, bool)
            and (reward.strip() != "" if isinstance(reward, str) else True)
        )
        has_stacking = tracker_stacking is not None

        if has_reward or has_stacking:
            raise ValidationError("У приятной привычки не может быть ни вознаграждения, ни связанной привычки")


class PeriodicityValidator:
    def __init__(self, periodicity: str):
        self.periodicity = periodicity

    def __call__(self, attrs: dict):
        value = attrs.get(self.periodicity)
        if value is None:
            return
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValidationError("Периодичность должна быть целым числом")
        if value < 1 or value > 7:
            raise ValidationError("Периодичность выполнения привычки должна быть от 1 до 7 дней")
