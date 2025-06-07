from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import logout
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Account
from .models import UserProfile
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now as djnow
from datetime import date
import pytz
from django.contrib.auth import update_session_auth_hash


def signin_view(request):
    context = {}
    if request.user.is_authenticated:
        return redirect('portal:index')
        # return HttpResponse('Hello')
    template = loader.get_template(str('account/authentications/signin.html'))
    return HttpResponse(template.render(context, request))


def sign_out_view(request):
    logout(request)
    return redirect('account:signin_view')


def sign_up_view(request):
    context = {'website_template': 'jetpro', "pagename": "Signup"}

    template = loader.get_template(str('account/authentications/signup.html'))
    return HttpResponse(template.render(context, request))


def forgot_password_view(request):
    context = {'website_template': 'jetpro', "pagename": "Signup"}
    template = loader.get_template(str('account/authentications/forgot_pass.html'))
    return HttpResponse(template.render(context, request))


@login_required
def change_password_view(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(old_password):
            messages.error(request, 'Mật khẩu cũ không chính xác.')
        elif new_password != confirm_password:
            messages.error(request, 'Xác nhận mật khẩu mới không khớp.')
        elif len(new_password) < 6:
            messages.error(request, 'Mật khẩu mới phải có ít nhất 6 ký tự.')
        else:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)  # ✅ giữ phiên đăng nhập
            messages.success(request, 'Đổi mật khẩu thành công!')
            return redirect('account:change_password_view')

    return render(request, 'account/authentications/change_password.html', {
        'current_menu': 'password',
        'breadcrumb_title': 'Đổi mật khẩu',
    })


@login_required
def my_profile_view(request):
    context = {}
    context['current_menu'] = 'profile'
    profile = UserProfile.objects.get(account=request.user)
    fullname = profile.get_full_name()
    context['fullname'] = fullname
    context['user'] = request.user
    context['profile'] = profile
    context['breadcrumb_title'] = 'Thông tin cá nhân'

    # print(fullname)
    template = loader.get_template(str('account/account_info/overview.html'))
    return HttpResponse(template.render(context, request))


@login_required
def profile_setting_view(request):
    profile = UserProfile.objects.get(account=request.user)

    if request.method == 'POST':
        profile.first_name = request.POST.get('first_name', '')
        profile.last_name = request.POST.get('last_name', '')
        profile.gender = request.POST.get('gender', '')
        profile.address = request.POST.get('address', '')
        profile.language = request.POST.get('language', 'en')
        profile.timezone = request.POST.get('timezone', 'Asia/Ho_Chi_Minh')
        request.user.telephone = request.POST.get('telephone', '')
        request.user.email = request.POST.get('email', '')

        # Ngày sinh
        try:
            day = int(request.POST.get('birth_day'))
            month = int(request.POST.get('birth_month'))
            year = int(request.POST.get('birth_year'))
            profile.birthday = date(year, month, day)
        except:
            profile.birthday = None

        # Ảnh đại diện
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']

        request.user.save()
        profile.save()
        return redirect('account:profile_setting_view')

    return render(request, 'account/account_info/profile_setting.html', {
        'profile': profile,
        'range_day': range(1, 32),
        'range_month': range(1, 13),
        'range_year': range(1950, date.today().year + 1),
        'timezones': [tz for tz in pytz.all_timezones if '/' in tz],
        'languages': [('en', 'English'), ('vi', 'Vietnam')],
        'current_menu': 'setting',
        'breadcrumb_title': 'Cài đặt hồ sơ',

    })

@login_required
def order_list_view(request):
    context = {}
    context['current_menu'] = 'orders'
    context['breadcrumb_title'] = 'Đơn hàng của tôi'
    template = loader.get_template(str('account/account_info/order_list.html'))
    return HttpResponse(template.render(context, request))



