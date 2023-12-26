from ast import List
import json
from django import forms
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import re

from django.utils import timezone

import requests
from utils.token import create_token
from .models import *
from manager.models import *

author_url = "https://api.openalex.org/authors"
institution_url = "https://api.openalex.org/institutions"
work_url = "https://api.openalex.org/works"
concept_url = "https://api.openalex.org/concepts"
source_url = "https://api.openalex.org/sources"


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

        repeated_name = User.objects.filter(user_name=username)
        if repeated_name.exists():
            return JsonResponse({"error": 4001, "msg": "用户名已存在"})

        repeated_email = User.objects.filter(email=email)
        if repeated_email.exists():
            return JsonResponse({"error": 4002, "msg": "邮箱已存在"})
        # 检测两次密码是否一致
        if password1 != password2:
            return JsonResponse({"error": 4003, "msg": "两次输入的密码不一致"})
        # 检测密码不符合规范：8-18，英文字母+数字
        print(type(password1))
        if not re.match("^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{8,18}$", password1):
            return JsonResponse({"error": 4004, "msg": "密码不符合规范"})

        new_user = User()
        new_user.user_name = username
        new_user.password = password1
        new_user.email = email
        new_user.save()

        token = create_token(username)
        return JsonResponse(
            {
                "error": 0,
                "msg": "注册成功!",
                "data": {
                    "userid": new_user.id,
                    "username": new_user.user_name,
                    "authorization": token,
                    "email": new_user.email,
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
                user = User.objects.get(user_name=username)
            except:
                return JsonResponse({"error": 4001, "msg": "用户名不存在"})
            if user.password != password:
                return JsonResponse({"error": 4002, "msg": "密码错误"})

            token = create_token(username)
            return JsonResponse(
                {
                    "error": 0,
                    "msg": "登录成功!",
                    "data": {
                        "userid": user.id,
                        "username": user.user_name,
                        "authorization": token,
                        "email": user.email,
                    },
                }
            )
        else:
            return JsonResponse({"error": 3001, "msg": "表单信息验证失败"})

    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def get_user_info(request):
    if request.method == "POST":
        userid = request.POST.get("userid")
        results = list(User.objects.filter(id=userid).values())
        return JsonResponse({"error": 0, "msg": "获取用户信息成功", "results": results})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def judge_scholar(request):
    if request.method == "POST":
        userid = request.POST.get("userid")
        scholar_id = request.POST.get("scholarId")
        results = User.objects.filter(id=userid).filter(scholar_id=scholar_id)
        if results.exists():
            return JsonResponse(
                {"error": 0, "msg": "用户已认证为指定学者", "results": results.exists()}
            )
        else:
            return JsonResponse(
                {"error": 0, "msg": "用户尚未认证为指定学者", "results": results.exists()}
            )
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


# 用户是否是认证用户
@csrf_exempt
def judge_authenticated(request):
    if request.method == "POST":
        userid = request.POST.get("userid")
        results = User.objects.filter(id=userid).exclude(scholar_id="")
        if results.exists():
            return JsonResponse(
                {"error": 0, "msg": "用户已认证", "results": results[0].scholar_id}
            )
        else:
            return JsonResponse(
                {"error": 0, "msg": "用户尚未认证", "results": results.exists()}
            )
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


# 学者是否被某个用户认证
@csrf_exempt
def scholar_get_user(request):
    if request.method == "POST":
        scholar_id = request.POST.get("scholarId")
        results = User.objects.filter(scholar_id=scholar_id)
        if results.exists():
            return JsonResponse(
                {"error": 0, "msg": "学者已被用户认证", "results": results[0].id}
            )
        else:
            return JsonResponse(
                {"error": 0, "msg": "学者尚未被用户认证", "results": results.exists()}
            )
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def concern_add(request):
    if request.method == "POST":
        userid = request.POST.get("userid")
        scholar_id = request.POST.get("scholarId")
        url = author_url + "/" + scholar_id + "?select=display_name"
        print(url)
        data = requests.get(url)
        display_name = data.json()["display_name"]
        new_concern = Concern()
        new_concern.user_id = userid
        new_concern.scholar_id = scholar_id
        new_concern.name = display_name
        new_concern.save()
        return JsonResponse({"error": 0, "msg": "添加关注成功"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def concern_delete(request):
    if request.method == "POST":
        userid = request.POST.get("userid")
        scholar_id = request.POST.get("scholarId")
        target = (
            Concern.objects.filter(user_id=userid)
            .filter(scholar_id=scholar_id)
            .filter(isDelete=False)
            .get()
        )
        print(target.isDelete)
        target.isDelete = True
        target.save()
        print(target.isDelete)
        return JsonResponse({"error": 0, "msg": "取消关注成功"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def get_all_concern(request):
    if request.method == "POST":
        userid = request.POST.get("userid")
        results = list(
            Concern.objects.filter(user_id=userid).filter(isDelete=0).values()
        )

        return JsonResponse({"error": 0, "msg": "获取关注列表成功", "results": results})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def judge_concern(request):
    if request.method == "POST":
        userid = request.POST.get("userid")
        scholarId = request.POST.get("scholarId")
        results = (
            Concern.objects.filter(user_id=userid)
            .filter(scholar_id=scholarId)
            .filter(isDelete=0)
        )

        if results.exists():
            return JsonResponse({"error": 0, "msg": "存在", "results": results.exists()})
        else:
            return JsonResponse({"error": 0, "msg": "不存在", "results": results.exists()})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def get_single_concern(request):
    if request.method == "POST":
        userid = request.POST.get("id")
        scholar_id = request.POST.get("scholarId")
        results = list(
            Concern.objects.filter(id=userid).filter(scholar_id=scholar_id).values()
        )
        return JsonResponse({"error": 0, "msg": "获取该关注成功", "results": results})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def label_star_add(request):
    if request.method == "POST":
        userid = request.POST.get("userid")
        lname = request.POST.get("name")
        label_temp = (
            Label.objects.filter(user_id=userid).filter(name=lname).filter(isDelete=0)
        )
        print(label_temp.exists())
        if label_temp.exists():
            return JsonResponse(
                {
                    "error": 0,
                    "msg": "标签重名",
                }
            )
        else:
            new_label = Label()
            new_label.user_id = userid
            new_label.name = lname

            new_label.save()
            return JsonResponse(
                {
                    "error": 0,
                    "msg": "添加标签成功",
                    "label": list(Label.objects.filter(id=new_label.id).values()),
                }
            )

    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def label_star_get_all(request):
    if request.method == "POST":
        userid = request.POST.get("userid")
        results = list(Label.objects.filter(user_id=userid).filter(isDelete=0).values())
        return JsonResponse({"error": 0, "msg": "获取所有标签成功", "results": results})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def label_star_get_single(request):
    if request.method == "POST":
        userid = request.POST.get("userid")
        id = request.POST.get("labelId")
        results = list(Label.objects.filter(user_id=userid).filter(id=id).values())
        return JsonResponse({"error": 0, "msg": "获取该标签成功", "results": results})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def label_delete(request):
    if request.method == "POST":
        userid = request.POST.get("userid")
        id = request.POST.get("id")
        is_delete = request.POST.get("isDelete")
        target = Label.objects.filter(user_id=userid).filter(id=id).get()
        target.isDelete = is_delete
        target.save()
        star_list = list(Star.objects.filter(user_id=userid).filter(label_id=id))
        for obj in star_list:
            obj.isDelete = is_delete
            obj.save()

        return JsonResponse({"error": 0, "msg": "删除标签成功"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def star_add(request):
    if request.method == "POST":
        userid = request.POST.get("userid")
        labelid = request.POST.get("labelId")
        articleid = request.POST.get("articleId")
        new_star = Star()
        new_star.user_id = userid
        new_star.label_id = labelid
        new_star.article_id = articleid
        url = (
            work_url
            + "/"
            + articleid
            + "?select=id,title,publication_date,cited_by_count,abstract_inverted_index"
        )
        print(url)
        data = requests.get(url)
        data1 = data.json()
        new_star.content = getAbstract(data1["abstract_inverted_index"])
        new_star.time = data1["publication_date"]
        new_star.title = data1["title"]
        new_star.cite_count = data1["cited_by_count"]
        url1 = work_url + "/" + articleid + "?select=authorships"
        data = requests.get(url1)
        data1 = data.json()
        authors_list = [
            authorship.get("author", {}) for authorship in data1["authorships"]
        ]
        temp = ArticleAuthor.objects.filter(article_id=articleid)
        if temp.exists():
            print(1)
        else:
            for obj in authors_list:
                new_link = ArticleAuthor()
                new_link.article_id = articleid
                new_link.scholar_name = obj["display_name"]
                new_link.save()

        new_star.save()
        return JsonResponse({"error": 0, "msg": "添加收藏成功", "data": authors_list})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def star_get_all(request):
    if request.method == "POST":
        userid = request.POST.get("userid")
        labelid = request.POST.get("labelId")
        results1 = list(
            Star.objects.filter(user_id=userid)
            .filter(label_id=labelid)
            .filter(isDelete=0)
            .values()
        )
        for obj in results1:
            author_temp = ArticleAuthor.objects.filter(article_id=obj["article_id"])
            if author_temp.exists():
                print(1)
        return JsonResponse({"error": 0, "msg": "获取该标签所有收藏成功", "results": results1})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def star_get_single(request):
    if request.method == "POST":
        userid = request.POST.get("userid")
        label_id = request.POST.get("labelId")
        id = request.POST.get("star_id")
        results = list(
            Star.objects.filter(user_id=userid)
            .filter(label_id=label_id)
            .filter(id=id)
            .values()
        )
        return JsonResponse({"error": 0, "msg": "获取该标签成功", "results": results})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def star_delete(request):
    if request.method == "POST":
        userid = request.POST.get("userid")
        labelid = request.POST.get("labelId")
        id = request.POST.get("id")
        target = (
            Star.objects.filter(user_id=userid)
            .filter(label_id=labelid)
            .filter(article_id=id)
            .get()
        )
        target.isDelete = True
        target.save()
        return JsonResponse({"error": 0, "msg": "取消收藏成功"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def history_add(request):
    if request.method == "POST":
        userid = request.POST.get("userid")
        type = request.POST.get("type")
        real_id = request.POST.get("realId")
        new_history = History()
        new_history.user_id = userid
        new_history.type = type
        new_history.real_id = real_id
        new_history.time = timezone.now()
        if type == "0":
            # 0为机构
            url1 = institution_url + "/" + real_id + "?select=display_name"
            data = requests.get(url1)
            data1 = data.json()["display_name"]
            new_history.name = data1
            new_history.save()
        if type == "1":
            # 1为文章
            url1 = work_url + "/" + real_id + "?select=display_name"
            data = requests.get(url1)
            data1 = data.json()["display_name"]
            new_history.name = data1
            new_history.save()
        if type == "2":
            # 2为学者
            url1 = author_url + "/" + real_id + "?select=display_name"
            data = requests.get(url1)
            data1 = data.json()["display_name"]
            new_history.name = data1
            new_history.save()
        return JsonResponse({"error": 0, "msg": "添加历史记录成功"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def History_get_all(request):
    if request.method == "POST":
        userid = request.POST.get("userid")
        results = list(
            History.objects.filter(user_id=userid)
            .filter(isDelete=0)
            .order_by("-id")
            .values()
        )
        return JsonResponse({"error": 0, "msg": "获取所有历史成功", "results": results})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def History_get_single(request):
    if request.method == "POST":
        userid = request.POST.get("userid")
        id = request.POST.get("id")
        results = list(History.objects.filter(user_id=userid).filter(id=id).values())
        return JsonResponse({"error": 0, "msg": "获取该历史记录成功", "results": results})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def History_delete_single(request):
    if request.method == "POST":
        userid = request.POST.get("userid")
        id = request.POST.get("id")
        is_delete = request.POST.get("isDelete")
        target = (
            History.objects.filter(user_id=userid).filter(id=id).filter(id=id).get()
        )
        target.isDelete = is_delete
        target.save()
        return JsonResponse({"error": 0, "msg": "删除该历史记录成功"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def History_delete_all(request):
    if request.method == "POST":
        userid = request.POST.get("userid")
        is_delete = request.POST.get("isDelete")
        history_list = list(History.objects.filter(user_id=userid))
        for obj in history_list:
            obj.isDelete = is_delete
            obj.save()
        return JsonResponse({"error": 0, "msg": "删除所有历史记录成功"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def apply_add(request):
    if request.method == "POST":
        userid = request.POST.get("userid")
        scholar_id = request.POST.get("scholarId")
        email = request.POST.get("email")
        content = request.POST.get("content")
        user_name = request.POST.get("username")
        scolarname = request.POST.get("scholarname")
        ins_name = request.POST.get("insname")
        new_apply = Application()
        new_apply.user_id = userid
        new_apply.scholar_id = scholar_id
        new_apply.email = email
        new_apply.content = content
        new_apply.time = timezone.now()
        new_apply.user_name = user_name
        new_apply.scholar_name = scolarname
        new_apply.ins_name = ins_name
        new_apply.save()
        return JsonResponse({"error": 0, "msg": "提交申请成功"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})


@csrf_exempt
def getAbstract(abstract_list):
    decoded_abstract = []
    if abstract_list is not None:
        for word, positions in abstract_list.items():
            for position in positions:
                decoded_abstract.append((word, position))
    # 对位置进行排序以还原顺序
    decoded_abstract.sort(key=lambda x: x[1])
    # 获取纯文本摘要
    final_abstract = " ".join([word for word, _ in decoded_abstract])
    return final_abstract
