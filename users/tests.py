from django.contrib.auth.hashers import check_password
from django.urls import NoReverseMatch, reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


def _resolve_url(candidates: list[str], fallback: str) -> str:
    for name in candidates:
        try:
            return reverse(name)
        except NoReverseMatch:
            continue
    return fallback


class UserAuthTests(APITestCase):
    def setUp(self):
        self.register_url = _resolve_url(
            ["users:register", "register", "user-register"],
            "/users/register/",
        )
        self.token_url = _resolve_url(
            ["users:token_obtain_pair", "token_obtain_pair"],
            "/users/token/",
        )
        self.refresh_url = _resolve_url(
            ["users:token_refresh", "token_refresh"],
            "/users/token/refresh/",
        )

        self.password = "StrongPass123!"
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "tg_chat_id": "123456789",
            "password": self.password,
        }

    def test_register_user_hashes_password_and_hides_it_in_response(self):
        response = self.client.post(self.register_url, self.user_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", response.data)
        self.assertEqual(response.data["email"], self.user_data["email"])
        self.assertEqual(response.data["username"], self.user_data["username"])
        self.assertEqual(response.data["tg_chat_id"], self.user_data["tg_chat_id"])

        user = User.objects.get(email=self.user_data["email"])
        self.assertNotEqual(user.password, self.password)
        self.assertTrue(check_password(self.password, user.password))

    def test_obtain_and_refresh_jwt_tokens(self):
        User.objects.create_user(
            username=self.user_data["username"],
            email=self.user_data["email"],
            password=self.password,
            tg_chat_id=self.user_data["tg_chat_id"],
        )

        token_response = self.client.post(
            self.token_url,
            {"email": self.user_data["email"], "password": self.password},
            format="json",
        )
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", token_response.data)
        self.assertIn("refresh", token_response.data)

        refresh_response = self.client.post(
            self.refresh_url,
            {"refresh": token_response.data["refresh"]},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)
