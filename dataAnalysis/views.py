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
concept_url = "https://api.openalex.org/concepts"
source_url = "https://api.openalex.org/sources"


# 主页部分
@csrf_exempt
def get_main_basic(request):
    url = work_url
    print(url)
    data = requests.get(url)
    data1 = data.json()["meta"]["count"]

    url1 = institution_url
    print(url1)
    data2 = requests.get(url1)
    data2 = data2.json()["meta"]["count"]

    url2 = author_url
    print(url2)
    data3 = requests.get(url2)
    data3 = data3.json()["meta"]["count"]

    url3 = concept_url
    print(url3)
    data4 = requests.get(url3)
    data4 = data4.json()["meta"]["count"]

    url4 = source_url
    print(url4)
    data5 = requests.get(url4)
    data5 = data5.json()["meta"]["count"]

    return JsonResponse(
        {
            "work_cout": data1,
            "institution_cout": data2,
            "author_count": data3,
            "concept_count": data4,
            "source_count": data5,
        }
    )


# 学者部分
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
    return JsonResponse({"error": 0, "msg": "成功!", "data": id_and_name_list})


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

    return JsonResponse({"error": 0, "msg": "成功!", "data": final_list})


# 学术成果部分
@csrf_exempt
def get_site_num(request):
    # 首先找学者最后一个隶属机构
    workid = request.POST.get("workId")

    url = work_url + "/" + workid + "?select=cited_by_count"
    print(url)
    data = requests.get(url)
    data1 = data.json()

    url1 = work_url + "/" + workid + "?select=counts_by_year"
    print(url1)
    data2 = requests.get(url1)
    data2 = data2.json()["counts_by_year"]
    return JsonResponse(
        {"error": 0, "msg": "成功!", "data": {"data1": data1, "data2": data2}}
    )


@csrf_exempt
def single_work_analysis(request):
    workid = request.POST.get("workId")
    count1 = 0
    count2 = 0
    url = (
        work_url
        + "/"
        + workid
        + "?select=cited_by_count,institutions_distinct_count,referenced_works,related_works,keywords,authorships,concepts,corresponding_institution_ids,counts_by_year"
    )
    print(url)
    data = requests.get(url)
    data1 = data.json()
    for obj in data1["referenced_works"]:
        count1 = count1 + 1
    for obj in data1["related_works"]:
        count2 = count2 + 1
    data1["reference_count"] = count1
    data1["related_count"] = count2
    authors_list = [authorship.get("author", {}) for authorship in data1["authorships"]]
    data1["authorships"] = authors_list
    return JsonResponse({"error": 0, "msg": "成功!", "data": data1})


@csrf_exempt
def muti_work_analysis(request):
    workid = request.POST.get("workId")
    workid = str(workid)
    workid = workid.split(",")
    str_temp = ""
    for i in workid:
        str_temp += i + "|"
    str_temp = str_temp[0 : len(str_temp) - 1]
    count1 = 0
    count2 = 0
    url = (
        work_url
        + "?filter=openalex:"
        + str_temp
        + "&select=cited_by_count,institutions_distinct_count,referenced_works,related_works,keywords,authorships,concepts,corresponding_institution_ids,counts_by_year"
    )
    data = requests.get(url)
    data1 = data.json()["results"]
    for obj in data1:
        for xfy in obj["referenced_works"]:
            count1 = count1 + 1
        for xfy in obj["related_works"]:
            count2 = count2 + 1
        obj["reference_count"] = count1
        count1 = 0
        obj["related_count"] = count2
        count2 = 0
        authors_list = [
            authorship.get("author", {}) for authorship in obj["authorships"]
        ]
        obj["authorships"] = authors_list
    return JsonResponse({"error": 0, "msg": "成功!", "data": data1})


# 机构部分
@csrf_exempt
def get_institution_basic(request):
    insid = request.POST.get("insId")

    url = (
        institution_url
        + "/"
        + insid
        + "?select=works_count,display_name,cited_by_count"
    )
    print(url)
    data = requests.get(url)
    data1 = data.json()["works_count"]
    display_name = data.json()["display_name"]

    data2 = data.json()["cited_by_count"]

    url2 = author_url + "?filter=last_known_institution.id:" + insid
    print(url2)
    data3 = requests.get(url2)
    data3 = data3.json()["meta"]["count"]

    url3 = (
        author_url
        + "?filter=last_known_institution.id:"
        + insid
        + "&sort=works_count:desc"
    )
    print(url3)
    data4 = requests.get(url3)
    data4 = data4.json()["results"][:20]
    name_list = [{"name": item["display_name"], "id": item["id"]} for item in data4]

    url4 = institution_url + "/" + insid + "?select=homepage_url"
    print(url4)
    data5 = requests.get(url4)
    data5 = data5.json()

    return JsonResponse(
        {
            "error": 0,
            "msg": "成功!",
            "data": {
                "work_cout": data1,
                "cite_cout": data2,
                "author_count": data3,
                "authors": name_list,
                "homepage_url": data5,
                "display_name": display_name,
            },
        }
    )


@csrf_exempt
def get_institution_range(request):
    insid = request.POST.get("insId")

    url = institution_url + "/" + insid + "?select=counts_by_year"
    print(url)
    data = requests.get(url)
    data1 = data.json()["counts_by_year"]
    year_and_cites_list = [
        {"year": item["year"], "cited_by_count": item["cited_by_count"]}
        for item in data1
    ]

    url1 = institution_url + "/" + insid + "?select=counts_by_year"
    print(url1)
    data2 = requests.get(url1)
    data2 = data2.json()["counts_by_year"]
    year_and_work_list = [
        {"year": item["year"], "works_count": item["works_count"]} for item in data2
    ]

    url2 = institution_url + "/" + insid + "?select=x_concepts&sort=score:desc"
    print(url2)
    data3 = requests.get(url2)
    data3 = data3.json()["x_concepts"]
    name_and_score_list = [
        {"display_name": item["display_name"], "score": item["score"]} for item in data3
    ]
    return JsonResponse(
        {
            "error": 0,
            "msg": "成功!",
            "data": {
                "cited_by_count": year_and_cites_list,
                "works_count": year_and_work_list,
                "score": name_and_score_list,
            },
        }
    )


@csrf_exempt
def get_institution_authors(request):
    insid = request.POST.get("insId")
    url = (
        author_url
        + "?filter=last_known_institution.id:"
        + insid
        + "&sort=works_count:desc"
        + "&sort=cited_by_count:desc"
    )
    print(url)
    data4 = requests.get(url)
    data4 = data4.json()["results"][:15]
    name_list = [
        {
            "name": item["display_name"],
            "works_conut": item["works_count"],
            "cited_by_count": item["cited_by_count"],
            "h_index": item["summary_stats"]["h_index"],
        }
        for item in data4
    ]
    return JsonResponse({"error": 0, "msg": "成功!", "data": name_list})
