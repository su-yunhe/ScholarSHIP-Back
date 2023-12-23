import aiohttp
import asyncio
import requests
from asgiref.sync import sync_to_async
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

base_url = "https://api.openalex.org/"


# 开始界面的文献初始查找
@csrf_exempt
def SearchWork(request):
    content = request.POST.get('content')
    page = request.POST.get('page')
    url = base_url + "works?search=" + content + "&filter=from_publication_date:2000-01-01,to_publication_date:" \
                                                 "2023-12-21&sort=cited_by_count:desc&per-page=20&page=" + page
    data = requests.get(url).json()
    # return JsonResponse({'data': data, 'meta': data["meta"]})
    result_list = []  # 用于存储结果的新列表
    organization = []
    # 获取所有索引结果
    for item in data["results"]:
        authors = []
        words = []
        work_id = []
        source = []
        location = []
        # 获取文件W开头的id
        index_of_last_slash = item["id"].rfind('/')
        if index_of_last_slash != -1:
            work_id = item["id"][index_of_last_slash + 1:]
        # 获取题目
        title = item["title"]
        # 获取组织：机构/出版社
        if item["primary_location"]:
            if item["primary_location"]["source"]:
                organization = item["primary_location"]["source"]["host_organization_name"]
                source = item["primary_location"]["source"]["display_name"]
        # 获取摘要、引用量、时间、关键词
        abstract = getAbstract(item["abstract_inverted_index"])
        cite = item["cited_by_count"]
        date = item["publication_date"]
        keywords = item["keywords"]
        for author_item in item["authorships"]:
            author = author_item["author"]["display_name"]
            authors.append(author)
        for keywords_item in keywords:
            word = keywords_item["keyword"]
            words.append(word)
        result_dict = {"id": work_id, "title": title, "abstract": abstract, "organization": organization,
                       "author": authors,
                       "cite": cite, "date": date, "keywords": words, "source": source}
        result_list.append(result_dict)
    return JsonResponse({'count': data["meta"]["count"], 'data': result_list, 'error': 0})


# 开始界面的学者初始查找
@csrf_exempt
def SearchAuthor(request):
    name = request.POST.get('name')
    page = request.POST.get("page")
    url = base_url + "authors?search=" + name + "&sort=cited_by_count:desc&per-page=20&page=" + page
    data = requests.get(url).json()
    result_list = []
    for item in data["results"]:
        index_of_last_slash = item["id"].rfind('/')
        author_id = item["id"][index_of_last_slash + 1:]
        author_name = item["display_name"]
        works_count = item["works_count"]
        cited_by_count = item["cited_by_count"]
        institution = None
        if item["last_known_institution"]:
            if item["last_known_institution"]["display_name"]:
                institution = item["last_known_institution"]["display_name"]
        concept = item["x_concepts"][0]["display_name"]
        result_dict = {"id": author_id, "name": author_name, "cite": cited_by_count, "works_count": works_count,
                       "institution": institution, "concept": concept}
        result_list.append(result_dict)
    return JsonResponse({'data': result_list, 'error': 0})


# 开始界面的机构初始查找
@csrf_exempt
def SearchInstitution(request):
    name = request.POST.get('name')
    page = request.POST.get("page")
    url = base_url + "institutions?search=" + name + "&sort=works_count:desc&per-page=20&page=" + page
    data = requests.get(url).json()
    result_list = []
    for item in data["results"]:
        concept_list = []
        index_of_last_slash = item["id"].rfind('/')
        institution_id = item["id"][index_of_last_slash + 1:]
        institution_name = item["display_name"]
        country = item["geo"]["country"]
        city = item["geo"]["city"]
        works_count = item["works_count"]
        cited_by_count = item["cited_by_count"]
        if item["x_concepts"]:
            if item["x_concepts"][0]["display_name"]:
                concept_list.append(item["x_concepts"][0]["display_name"])
            if item["x_concepts"][1]["display_name"]:
                concept_list.append(item["x_concepts"][1]["display_name"])
            if item["x_concepts"][2]["display_name"]:
                concept_list.append(item["x_concepts"][2]["display_name"])
        result_dict = {"id": institution_id, "name": institution_name, "country": country, "city": city,
                       "cite": cited_by_count, "works_count": works_count, "concept": concept_list}
        result_list.append(result_dict)
    return JsonResponse({'data': result_list, 'error': 0})


# 获取前十名作者
@csrf_exempt
def getTopAuthor(request):
    content = request.POST.get('content')
    url = base_url + "works?filter=title.search:" + content + "&group_by=author.id&sort=count:desc&per-page=11"
    data = requests.get(url).json()
    # 获取前十名作者
    author_list = []
    for item in data["group_by"]:
        author_name = item["key_display_name"]
        count = item["count"]
        author = {"name": author_name, "count": count}
        author_list.append(author)
    return JsonResponse({'top_author': author_list, 'error': 0})


# 获取前十名机构
@csrf_exempt
def getTopInstitution(request):
    content = request.POST.get('content')
    url = base_url + "works?filter=title.search:" + content + "&group_by=institution.id&sort=count:desc&per-page=10"
    data = requests.get(url).json()
    institution_list = []
    for item in data["group_by"]:
        institution_name = item["key_display_name"]
        count = item["count"]
        institution = {"name": institution_name, "count": count}
        institution_list.append(institution)
    return JsonResponse({'top_institution': institution_list, 'error': 0})


# 获取前十名概念
@csrf_exempt
def getTopConcept(request):
    content = request.POST.get('content')
    url = base_url + "works?filter=title.search:" + content + "&group_by=concepts.id&sort=count:desc&per-page=10"
    data = requests.get(url).json()
    concept_list = []
    for item in data["group_by"]:
        concept_name = item["key_display_name"]
        count = item["count"]
        concept = {"name": concept_name, "count": count}
        concept_list.append(concept)
    return JsonResponse({'top_concept': concept_list, 'error': 0})


# 获取纯文本摘要
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
    final_abstract = ' '.join([word for word, _ in decoded_abstract])
    return final_abstract


# # 高级检索
# @csrf_exempt
# async def AdvancedSearchWork(request):  # op = 0 , op=1 且，op=2 或，op=3非 #type:1、2、3、4对应title、author、机构、概念
#     print(1)
#     search_list = [{"op": 0, "type": 1, "name": "software"},
#                    {"op": 1, "type": 3, "name": "Beihang University"},
#                    {"op": 2, "type": 3, "name": "Peking University"},
#                    {"op": 0, "type": 4, "name": "software"}, ]
#
#     title_list = []
#     for item in search_list:
#         url_institution = []
#         url_author = []
#         url_concept = []
#         op = item["op"]
#         type = item["type"]
#         name = item["name"]
#         if type == 1:
#             title_list.append(name)
#         elif type == 2:
#
#     work_name = "software"
#     author_name = "Tom"
#     institution_name = "Beihang University"
#     concept_name = "artificial"
#
#     url_institution = base_url + "institutions?search=" + institution_name + "&select=id&per-page=50"
#     url_author = base_url + "authors?search=" + author_name + "&select=id&per-page=50"
#     url_concept = base_url + "concepts?search=" + concept_name + "&select=id&per-page=1"
#
#     tasks = [fetch_data(url_institution), fetch_data(url_author)]
#     data1, data2 = await asyncio.gather(*tasks)

    # 拼接institution部分
    # data_institution = requests.get(url_institution).json()
    # institution_list = data_institution["results"]
    # url_institution = ",institution.id:"
    # for item in institution_list:
    #     index_of_last_slash = item["id"].rfind('/')
    #     institution_id = item["id"][index_of_last_slash + 1:]
    #     url_institution += institution_id + "|"
    # url_institution = url_institution[:-1]
    #
    # # 拼接author部分
    # data_author = requests.get(url_author).json()
    # author_list = data_author["results"]
    # url_author = ",authorships.author.id:"
    # for item in author_list:
    #     index_of_last_slash = item["id"].rfind('/')
    #     author_id = item["id"][index_of_last_slash + 1:]
    #     url_author += author_id + "|"
    # url_author = url_author[:-1]
    #
    # # 拼接url进行搜索
    # url = base_url + "works?filter=title.search:" + work_name + url_institution + url_author
    # print(url)
    # data = requests.get(url).json()
    # return JsonResponse({'data': data})


async def fetch_data(url):
    async with aiohttp.ClientSession() as client:
        async with client.get(url) as response:
            return await response.json()


# 获取文献原地址
@csrf_exempt
def getWorkLocation(request):
    work_id = request.POST.get('id')
    url = base_url + "works/" + work_id
    data = requests.get(url).json()
    location = []
    if data["primary_location"]:
        if data["primary_location"]["landing_page_url"]:
            location = data["primary_location"]["landing_page_url"]
    return JsonResponse({'data': location, 'error': 0})


# 获取pdf下载地址
@csrf_exempt
def DownloadWork(request):
    work_id = request.POST.get('id')
    url = base_url + "works/" + work_id
    data = requests.get(url).json()
    location = []
    if data["primary_location"]:
        if data["primary_location"]["pdf_url"]:
            location = data["primary_location"]["pdf_url"]
    return JsonResponse({'data': location, 'error': 0})
