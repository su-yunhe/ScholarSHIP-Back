from django.shortcuts import render
from django import forms
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import re
from utils.token import create_token
from .models import Manager


class RegisterForm(forms.Form):
    userName = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput())
    password1 = forms.CharField(
        label="密码", max_length=128, widget=forms.PasswordInput()
    )
    password2 = forms.CharField(
        label="确认密码", max_length=128, widget=forms.PasswordInput()
    )
    email = forms.EmailField(label="个人邮箱", widget=forms.EmailInput())


class LoginForm(forms.Form):
    userName = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput())
    password = forms.CharField(label="密码", max_length=128, widget=forms.PasswordInput())


@csrf_exempt
def register(request):
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        # if register_form.is_valid():
        print(register_form)
        username = register_form.cleaned_data.get("userName")
        password1 = register_form.cleaned_data.get("password1")
        password2 = register_form.cleaned_data.get("password2")
        email = register_form.cleaned_data.get("email")

        repeated_name = Manager.objects.filter(admin_name=username)
        if repeated_name.exists():
            return JsonResponse({"error": 4001, "msg": "用户名已存在"})

        repeated_email = Manager.objects.filter(email=email)
        if repeated_email.exists():
            return JsonResponse({"error": 4002, "msg": "邮箱已存在"})
        # 检测两次密码是否一致
        if password1 != password2:
            return JsonResponse({"error": 4003, "msg": "两次输入的密码不一致"})
        # 检测密码不符合规范：8-18，英文字母+数字
        if not re.match("^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{8,18}$", password1):
            return JsonResponse({"error": 4004, "msg": "密码不符合规范"})

        new_manager = Manager()
        new_manager.admin_name = username
        new_manager.password = password1
        new_manager.email = email
        new_manager.save()

        token = create_token(username)
        return JsonResponse(
            {
                "error": 0,
                "msg": "注册成功!",
                "data": {
                    "id": new_manager.id,
                    "admin_name": new_manager.admin_name,
                    "authorization": token,
                    "email": new_manager.email,
                },
            }
        )

        # else:
        #     return JsonResponse({'error': 3001, 'msg': '表单信息验证失败'})

    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def login(request):
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        print("111")
        print(login_form)
        if login_form.is_valid():
            username = login_form.cleaned_data.get("userName")
            password = login_form.cleaned_data.get("password")
            print(username)
            try:
                admin = Manager.objects.get(admin_name=username)
            except:
                return JsonResponse({"error": 4001, "msg": "用户名不存在"})
            if admin.password != password:
                return JsonResponse({"error": 4002, "msg": "密码错误"})

            token = create_token(username)
            return JsonResponse(
                {
                    "error": 0,
                    "msg": "登录成功!",
                    "data": {
                        "id": admin.id,
                        "amdin_name": admin.admin_name,
                        "authorization": token,
                        "email": admin.email,
                    },
                }
            )
        else:
            return JsonResponse({"error": 3001, "msg": "表单信息验证失败"})

    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


# Create your views here.
