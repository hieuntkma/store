import json
import random

from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import *
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


#### admin #####
@user_passes_test(lambda u: u.is_superuser)
@login_required(login_url='account:signin')
def admin_get_all_user(request):
    try:
        accounts = Account.objects.all().order_by('-created_at')
        results = []

        for account in accounts:
            try:
                profile = UserProfile.objects.get(account=account)
                full_name = profile.get_full_name() or ''
                avatar = profile.avatar.url if profile.avatar else ''
            except UserProfile.DoesNotExist:
                full_name = ''
                avatar = ''

            results.append({
                'uuid': str(account.uuid),
                'username': account.username,
                'email': account.email,
                'telephone': account.telephone,
                'is_superuser': account.is_superuser,
                'is_active': account.is_active,
                'is_verified': account.is_verified,
                'created_at': account.created_at,
                'full_name': full_name,
                'avatar': avatar
            })

        return JsonResponse({'status': 'success', 'users': results}, status=200)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Lỗi xảy ra: {str(e)}'}, status=500)


@login_required(login_url='account:signin')
@user_passes_test(lambda u: u.is_superuser)
def admin_create_user_api_view(request):
    try:
        data = json.loads(request.body)

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        is_superuser = data.get('is_superuser', False)

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
            is_superuser=is_superuser,
            is_active=True  # Cho phép login ngay không cần verify
        )

        return JsonResponse({'success': True, 'message': 'Account created successfully'}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON.'}, status=400)


@login_required(login_url='account:signin')
@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(["GET", "POST", "PUT"])
def admin_edit_user_api_view(request, user_uuid):
    try:
        from account.models import Account  # hoặc thay theo app bạn dùng

        try:
            user = Account.objects.get(uuid=user_uuid)
        except Account.DoesNotExist:
            return JsonResponse({"error": "Không tìm thấy người dùng."}, status=404)

        # Trả dữ liệu để edit
        if request.method == "GET":
            data = {
                "uuid": str(user.uuid),
                "username": user.username,
                "email": user.email,
                # "avatar": user.avatar,
                "is_superuser": user.is_superuser,
            }
            return JsonResponse(data)

        # Xử lý cập nhật
        elif request.method in ["POST", "PUT"]:
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Dữ liệu không hợp lệ."}, status=400)

            username = data.get("username")
            email = data.get("email")
            password = data.get("password")
            is_superuser = data.get("is_superuser", False)

            if not username:
                return JsonResponse({"error": "Tên đăng nhập không được bỏ trống."}, status=400)

            # Kiểm tra trùng tên username
            if Account.objects.filter(username=username).exclude(uuid=user_uuid).exists():
                return JsonResponse({"error": "Tên đăng nhập đã tồn tại."}, status=400)

            user.username = username
            user.email = email or ""
            user.is_superuser = is_superuser

            if password:
                user.set_password(password)

            user.save()

            return JsonResponse({
                "success": True,
                "message": "Cập nhật người dùng thành công.",
                "data": {
                    "uuid": str(user.uuid),
                    "username": user.username,
                    "email": user.email,
                    "is_superuser": user.is_superuser
                }
            })

    except Exception as e:
        return JsonResponse({"error": f"Lỗi hệ thống: {str(e)}"}, status=500)


@require_POST
@login_required(login_url='account:signin')
@user_passes_test(lambda u: u.is_superuser)
def admin_delete_user_api_view(request, user_uuid):
    try:
        try:
            user = Account.objects.get(uuid=user_uuid)
        except Account.DoesNotExist:
            return JsonResponse({'error': 'Người dùng không tồn tại.'}, status=404)

        # Không cho xóa chính mình
        if request.user.uuid == user.uuid:
            return JsonResponse({'error': 'Bạn không thể xóa chính mình.'}, status=400)

        user.delete()

        return JsonResponse({'status': 'success', 'message': 'Người dùng đã được xóa.'}, status=200)

    except Exception as e:
        return JsonResponse({'error': f'Lỗi xảy ra: {str(e)}'}, status=500)
