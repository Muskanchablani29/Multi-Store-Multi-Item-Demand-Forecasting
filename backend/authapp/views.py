from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()
        full_name = request.data.get('full_name', '').strip()

        if not username or not password:
            return Response({'error': 'username and password are required'}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already taken'}, status=400)

        first, *last = full_name.split(' ', 1) if full_name else ('', [])
        user = User.objects.create_user(
            username=username, password=password,
            first_name=first, last_name=last[0] if last else ''
        )
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': _user_data(user),
        }, status=201)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        from django.contrib.auth import authenticate
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()
        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'Invalid credentials'}, status=401)
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': _user_data(user),
        })


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(_user_data(request.user))


def _user_data(user):
    shop = None
    try:
        s = user.shop
        shop = {
            'id': s.id,
            'shop_id': s.shop_id,
            'name': s.name,
            'location': s.location,
            'category': s.category,
        }
    except Exception:
        pass
    return {
        'id': user.id,
        'username': user.username,
        'full_name': user.get_full_name(),
        'shop': shop,
    }
