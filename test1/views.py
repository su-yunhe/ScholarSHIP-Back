from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from test1.models import *
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def test_add(request):
    if request.method == "POST":
        include= request.POST.get("include")
        new_test = Test()
        new_test.include=include
        new_test.save()
        return JsonResponse({"error": 0, "msg": "新建成功"})
    else:
        return JsonResponse({"error": 2001, "msg": "请求方式错误"})