from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from users.models import User
from users.serializers import UserRegisterSerializer

# Create your views here.


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserRegisterSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]
