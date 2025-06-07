import json
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Account
import datetime


@require_POST
def signin_api_view(request):
    try:
        data = json.loads(request.body)
        identifier = data.get('email')  # có thể là email hoặc username
        password = data.get('password')

        if not identifier or not password:
            return JsonResponse({'success': False, 'message': 'Email/Username and password are required'}, status=400)

        # Tìm tài khoản bằng email hoặc username
        obj = Account.objects.filter(email=identifier).first()
        if not obj:
            obj = Account.objects.filter(username=identifier).first()

        if not obj:
            return JsonResponse({'success': False, 'message': 'Account not found'}, status=404)

        if not obj.is_active:
            return JsonResponse({'success': False, 'message': 'Account is not active. Please verify your email.'},
                                status=400)

        # Xác thực
        user = authenticate(request, username=obj.username, password=password)

        if user:
            login(request, user)
            return JsonResponse({'success': True, 'message': 'Login successful'})

        return JsonResponse({'success': False, 'message': 'Invalid credentials'}, status=401)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON.'}, status=400)


# TODO: Black_list to check ip
@require_POST
def signup_api_view(request):
    try:
        data = json.loads(request.body)

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        # Kiểm tra thông tin thiếu
        missing_fields = [field for field in ['username', 'email', 'password', 'first_name', 'last_name'] if
                          not data.get(field)]
        if missing_fields:
            return JsonResponse({'success': False, 'message': f"Missing fields: {', '.join(missing_fields)}"},
                                status=400)

        # Kiểm tra username hoặc email đã tồn tại
        if Account.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'message': 'Username already exists'}, status=400)

        if Account.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'Email already exists'}, status=400)

        # Tạo tài khoản
        Account.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=True  # Cho phép login ngay không cần verify
        )

        return JsonResponse({'success': True, 'message': 'Account created successfully'}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON.'}, status=400)

@login_required
def deactivate_user_api(request):
    user = request.user

    # Cập nhật trạng thái
    user.is_active = False
    user.deactivated_at = timezone.now()

    user.save()

    return JsonResponse({'success': True, 'message': 'Account deactivated successfully'})

@csrf_exempt
def user_info_test_api_view(request):
    data = {
        'name': 'Nguyen Van A',
        'email': 'nguyenvana@example.com',
        'phone': '0123456789',
    }
    return JsonResponse(data)

