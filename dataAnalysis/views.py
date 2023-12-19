import json
from django.shortcuts import render
from django import forms
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import re

import requests
from utils.token import create_token
from .models import *
from user.models import *

author_url = "https://api.openalex.org/authors"
institution_url = "https://api.openalex.org/institutions"
work_url = "https://api.openalex.org/works"


@csrf_exempt
def get_author_college(request):
    # 首先找学者最后一个隶属机构
    author_id = request.POST.get("authorId")
    url = (
        author_url + "/" + author_id + "?select=id,display_name,last_known_institution"
    )
    # print(url)
    data = requests.get(url)
    res = json.dumps(data.json())
    data1 = data.json()
    # 然后找这个机构里的其他人
    last_known_institution = data1["last_known_institution"]["id"]
    print(last_known_institution)
    url1 = author_url + "?filter=last_known_institution.id:" + last_known_institution
    data = requests.get(url1)
    res = json.dumps(data.json())
    data1 = data.json()["results"]
    id_and_name_list = [
        {"id": item["id"], "name": item["display_name"]} for item in data1
    ]
    return JsonResponse({"data": id_and_name_list})


@csrf_exempt
def get_author_partner(request):
    # 首先找学者最近五篇文章
    author_id = request.POST.get("authorId")
    url = (
        work_url
        + "?filter=author.id:"
        + author_id
        + "&sort=publication_date:desc&select=id,display_name"
    )
    data = requests.get(url)
    res = json.dumps(data.json())
    data1 = data.json()["results"][:5]
    final_list = list()
    for obj in data1:
        url = work_url + "/" + obj["id"] + "?select=authorships"
        data = requests.get(url)
        data1 = data.json()
        # print(list(data1["authorships"]))
        authors_list = [
            authorship.get("author", {}) for authorship in data1["authorships"]
        ]
        for obj in authors_list:
            if obj not in final_list:
                final_list.append(obj)
        # print(authors_list)

    return JsonResponse({"data": final_list})
