from datetime import time
from django.urls import NoReverseMatch, reverse
from rest_framework import status
from rest_framework.test import APITestCase
from tracker.models import Tracker
from users.models import User


def _resolve_url(candidates: list[str], fallback: str, kwargs: dict | None = None) -> str:
    for name in candidates:
        try:
            return reverse(name, kwargs=kwargs)
        except NoReverseMatch:
            continue
    if kwargs and "pk" in kwargs:
        return f"{fallback.rstrip('/')}/{kwargs['pk']}/"
    return fallback


class TrackerApiAndLogicTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="Password123!",
            tg_chat_id="111111",
        )
        self.other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="Password123!",
            tg_chat_id="222222",
        )

        self.list_url = _resolve_url(
            ["tracker:tracker-list", "tracker-list", "trackers-list"],
            "/trackers/",
        )
        self.public_url = _resolve_url(
            ["tracker:public-list", "tracker:tracker-public", "public-list", "public"],
            "/public/",
        )

        self.pleasant_habit = Tracker.objects.create(
            user=self.user,
            place="Дома",
            time=time(8, 0),
            action="Выпить чашку чая",
            pleasant_tracker=True,
            periodicity=1,
            completion_time=30,
            publicness=True,
        )
        self.useful_habit = Tracker.objects.create(
            user=self.user,
            place="В зале",
            time=time(9, 30),
            action="Сделать разминку",
            pleasant_tracker=False,
            tracker_stacking=self.pleasant_habit,
            periodicity=1,
            completion_time=60,
            publicness=False,
        )
        self.other_habit = Tracker.objects.create(
            user=self.other_user,
            place="Офис",
            time=time(11, 0),
            action="Проверить задачи",
            pleasant_tracker=False,
            reward="Кофе",
            periodicity=2,
            completion_time=45,
            publicness=False,
        )

    def _detail_url(self, pk: int) -> str:
        return _resolve_url(
            ["tracker:tracker-detail", "tracker-detail", "trackers-detail"],
            "/trackers/",
            kwargs={"pk": pk},
        )

    def _auth_user(self, user: User):
        self.client.force_authenticate(user=user)

    def test_anonymous_cannot_access_trackers_or_public(self):
        self.assertEqual(self.client.get(self.list_url).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.get(self.public_url).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_tracker_assigns_current_user(self):
        self._auth_user(self.user)
        payload = {
            "place": "Парк",
            "time": "18:00:00",
            "action": "Пробежать 2 км",
            "pleasant_tracker": False,
            "reward": "Смузи",
            "periodicity": 2,
            "completion_time": 90,
            "publicness": True,
        }
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created = Tracker.objects.get(pk=response.data["id"])
        self.assertEqual(created.user, self.user)
        self.assertEqual(created.action, "Пробежать 2 км")

    def test_list_returns_only_own_habits_and_public_returns_public_only(self):
        self._auth_user(self.user)

        my_response = self.client.get(self.list_url)
        self.assertEqual(my_response.status_code, status.HTTP_200_OK)
        results = my_response.data.get("results", my_response.data)
        returned_ids = {item["id"] for item in results}
        self.assertIn(self.pleasant_habit.id, returned_ids)
        self.assertIn(self.useful_habit.id, returned_ids)
        self.assertNotIn(self.other_habit.id, returned_ids)

        public_response = self.client.get(self.public_url)
        self.assertEqual(public_response.status_code, status.HTTP_200_OK)
        pub_results = public_response.data.get("results", public_response.data)
        pub_ids = {item["id"] for item in pub_results}
        self.assertIn(self.pleasant_habit.id, pub_ids)
        self.assertNotIn(self.other_habit.id, pub_ids)

    def test_other_user_cannot_update_or_delete_someone_elses_habit(self):
        self._auth_user(self.other_user)
        detail_url = self._detail_url(self.useful_habit.id)

        patch_resp = self.client.patch(detail_url, {"action": "Взлом"}, format="json")
        self.assertIn(patch_resp.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))

        delete_resp = self.client.delete(detail_url)
        self.assertIn(delete_resp.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))
        self.assertTrue(Tracker.objects.filter(pk=self.useful_habit.id).exists())

    def test_pagination_default_size_and_page_size_param(self):
        self._auth_user(self.user)
        for idx in range(6):
            Tracker.objects.create(
                user=self.user,
                place="Дом",
                time=time(7, 0),
                action=f"Привычка #{idx}",
                pleasant_tracker=False,
                reward="Чай",
                periodicity=1,
                completion_time=30,
            )

        resp_default = self.client.get(self.list_url)
        self.assertEqual(resp_default.status_code, status.HTTP_200_OK)
        self.assertIn("results", resp_default.data)
        self.assertEqual(len(resp_default.data["results"]), 5)

        resp_custom = self.client.get(f"{self.list_url}?page_size=2")
        self.assertEqual(resp_custom.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp_custom.data["results"]), 2)

    def test_validators_reject_invalid_combinations_and_values(self):
        self._auth_user(self.user)
