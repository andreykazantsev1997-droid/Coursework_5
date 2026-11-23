from celery import shared_task
from django.utils import timezone

from tracker.models import Tracker
from tracker.services import send_telegram_message


@shared_task
def send_habit_reminders():
    now = timezone.localtime()
    trackers = (
        Tracker.objects.select_related("user")
        .filter(
            time__hour=now.hour,
            time__minute=now.minute,
        )
        .exclude(user__tg_chat_id__isnull=True)
        .exclude(user__tg_chat_id="")
    )

    sent_count = 0
    for item in trackers:
        text = (
            f"Я буду {item.action} в "
            f"{item.time.strftime('%H:%M')} в {item.place}"
        )
        send_telegram_message(chat_id=item.user.tg_chat_id, text=text)
        sent_count += 1

    return f"Отправлено напоминаний: {sent_count}"