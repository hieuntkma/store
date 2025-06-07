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
# #from .models import Account
import datetime

@require_POST
def signin_api_view(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return JsonResponse({'success': False, 'message': 'Email and password are required'}, status=400)

        # Tìm tài khoản với email
        obj = Account.objects.filter(email=email).first()

        if not obj:
            return JsonResponse({'success': False, 'message': 'Email not found'}, status=404)

        # Kiểm tra tài khoản đã được kích hoạt hay chưa
        if not obj.is_active:
            return JsonResponse({'success': False, 'message': 'Account is not active. Please verify your email.'},
                                status=400)

        # Xác thực người dùng với username và password
        user = authenticate(request, username=obj.username, password=password)

        if user:
            login(request, user)
            return JsonResponse({'success': True, 'message': 'Login successful'})

        return JsonResponse({'success': False, 'message': 'Invalid email or password'}, status=401)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON.'}, status=400)


# TODO: Black_list to check ip
@require_POST
def signup_api_view(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        # Kiểm tra đầy đủ thông tin
        missing_fields = [field for field in ['email', 'password', 'first_name', 'last_name'] if not data.get(field)]
        if missing_fields:
            return JsonResponse({'success': False, 'message': f"Missing fields: {', '.join(missing_fields)}"},
                                status=400)

        # Kiểm tra email đã tồn tại
        if Account.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'Email already exist'}, status=400)

        # Tạo user mới
        Account.objects.create_user(
            username=email.split("@")[0],
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=False,
        )

        otp = str(random.randint(100000, 999999))

        cache.set(f"otp:signup:{email}", otp, timeout=300)

        try:
            send_mail(
                subject='Xác thực tài khoản',
                message=f'Mã otp của bạn là: {otp}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending email: {e}")

        # Lưu email vào session
        request.session['otp_email'] = email
        request.session['otp_purpose'] = 'signup'

        return JsonResponse({'success': True, 'message': 'Signup successful. OTP sent to email'}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON.'}, status=400)


@require_POST
def verify_otp_api(request):
    try:
        data = json.loads(request.body)
        otp_input = data.get('otp')

        if not otp_input:
            return JsonResponse({'success': False, 'message': 'Missing OTP'}, status=400)

        # Lấy email từ session
        email = request.session.get('otp_email')
        purpose = request.session.get('otp_purpose')
        if not email or not purpose:
            return JsonResponse({'success': False, 'message': 'Session expired or invalid.'}, status=400)

        otp_stored = cache.get(f'otp:{purpose}:{email}')
        if not otp_stored:
            return JsonResponse({'success': False, 'message': 'OTP expired or not found. Please request a new OTP.'},
                                status=400)

        if otp_input != otp_stored:
            return JsonResponse({'success': False, 'message': 'Invalid OTP'}, status=400)

        if purpose == 'signup':
            try:
                user = Account.objects.get(email=email)
                user.is_active = True
                user.is_verified = True
                user.save()
            except Account.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'User not found'}, status=404)

        elif purpose == 'change_email':
            if not request.user.is_authenticated:
                return JsonResponse({'success': False, 'message': 'Authentication required'}, status=403)

            request.user.email = email
            request.user.username = email.split("@")[0]
            request.user.is_verified = True
            request.user.save()

        else:
            return JsonResponse({'success': False, 'message': 'Unknown OTP purpose'}, status=400)

        cache.delete(f'otp:{purpose}:{email}')
        request.session.pop('otp_email', None)
        request.session.pop('otp_purpose', None)

        return JsonResponse({'success': True, 'message': 'OTP verified'}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)


@login_required
def change_password_api(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)

    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return JsonResponse({'success': False, 'message': 'Missing fields'}, status=400)

    user = request.user

    # Kiểm tra mật khẩu cũ
    if not user.check_password(old_password):
        return JsonResponse({'success': False, 'message': 'Invalid password'}, status=400)

    # Đổi mật khẩu
    user.set_password(new_password)
    user.save()

    return JsonResponse({'success': True, 'message': 'Change password successfully'}, status=200)


# TODO: my_settings, user_config
@require_POST
@login_required
def update_profile_api(request):
    user = request.user
    profile = user.userprofile

    # Lấy dữ liệu từ form
    profile.first_name = request.POST.get('first_name', '')
    profile.last_name = request.POST.get('last_name', '')
    profile.name = f"{profile.last_name} {profile.first_name}".strip()
    profile.gender = request.POST.get('gender', '')
    profile.address = request.POST.get('address', '')
    profile.language = request.POST.get('language', '')
    profile.timezone = request.POST.get('timezone', '')
    # Cập nhật thông báo trực tiếp và thông báo qua email
    profile.setting_notification_direct = request.POST.get('setting_notification_direct', '') == 'on'
    profile.setting_notification_email = request.POST.get('setting_notification_email', '') == 'on'

    # Avatar nếu có
    if 'avatar' in request.FILES:
        profile.avatar = request.FILES['avatar']

    # Ngày sinh
    birthday = request.POST.get('birthday')
    if birthday:
        try:
            from datetime import datetime
            profile.birthday = datetime.strptime(birthday, "%Y-%m-%d").date()
        except ValueError:
            pass  # Có thể báo lỗi nếu muốn

    profile.save()
    user.first_name = profile.first_name
    user.last_name = profile.last_name
    user.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Update profile successfully'})


@require_POST
@login_required
def change_email_api(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)

    # Get password, new email
    current_password = data.get('password')
    new_email = data.get('new_email')

    if not new_email or not current_password:
        return JsonResponse({'success': False, 'message': 'Missing required fields (new_email, password)'}, status=400)

    # Kiểm tra xem email mới có tồn tại trong hệ thống không
    if Account.objects.filter(email=new_email).exists():
        return JsonResponse({'success': False, 'message': 'Email already exists'}, status=400)

    try:
        # Lấy user hiện tại
        user = request.user

        # Kiểm tra mật khẩu hiện tại
        if not user.check_password(current_password):
            return JsonResponse({'success': False, 'message': 'Password is incorrect'}, status=400)

        # Cập nhật email mới
        user.email = new_email
        user.username = new_email.split('@')[0]
        user.is_verified = False
        user.save()

        user.refresh_from_db()

        return JsonResponse({'success': True, 'message': 'Email changed successfully', 'is_verified': user.is_verified,})

    except Account.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'}, status=404)


@require_POST
@login_required
def verify_email_api(request):
    try:
        data = json.loads(request.body)
        new_email = data.get('new_email')

        if not new_email:
            return JsonResponse({'success': False, 'message': 'Missing new_email'}, status=400)

        otp = str(random.randint(100000, 999999))
        cache.set(f'otp:change_email:{new_email}', otp, timeout=300)

        send_mail(
            subject='Xác nhận thay đổi email',
            message=f'Mã OTP của bạn là: {otp}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[new_email],
            fail_silently=False,
        )

        request.session['otp_email'] = new_email
        request.session['otp_purpose'] = 'change_email'

        return JsonResponse({'success': True, 'message': 'OTP sent to new email'}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)

@login_required
def deactivate_user_api(request):
    user = request.user

    # Cập nhật trạng thái
    user.is_active = False
    user.deactivated_at = timezone.now()

    user.save()

    return JsonResponse({'success': True, 'message': 'Account deactivated successfully'})


@csrf_exempt
def mock_user_activity_api(request):
    sample_data = [
        {
            "username": "admin",
            "action": "login",
            "target_model": "User",
            "created_at": datetime.datetime.now().isoformat()
        },
        {
            "username": "johndoe",
            "action": "update",
            "target_model": "Post",
            "created_at": (datetime.datetime.now() - datetime.timedelta(minutes=10)).isoformat()
        },
        {
            "username": "janedoe",
            "action": "delete",
            "target_model": "Comment",
            "created_at": (datetime.datetime.now() - datetime.timedelta(hours=1)).isoformat()
        },
    ]
    return JsonResponse(sample_data, safe=False)

