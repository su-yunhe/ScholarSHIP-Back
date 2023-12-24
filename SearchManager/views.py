import aiohttp
import asyncio
import requests
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
    getWorkDetails(url)
    result_list = getWorkDetails(url)
    return JsonResponse({'data': result_list, 'error': 0})


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


# 高级检索
@csrf_exempt
def AdvancedSearchWork(request):  # op = 0是非 ,op=1  #type:1、2、3、4对应title、author、机构、概念
    print(1)
    search = request.POST.get("search")
    search_list = search["search_list"]
    min_year = search["min_year"]
    max_year = search["max_year"]
    # search_list = [{"op": 1, "type": 2, "name": "song"},
    #                {"op": 1, "type": 3, "name": "Peking"},
    #                {"op": 0, "type": 3, "name": "beihang"},
    #                {"op": 1, "type": 1, "name": "software"},
    #                {"op": 1, "type": 4, "name": "network"}]
    # min_year = 2000
    # max_year = 2015
    title_list = []
    concept_list = []
    institution_list = []
    author_list = []
    for item in search_list:
        type = item["type"]
        op = item["op"]
        if type == 1:
            title_list.append({"name": item["name"], "op": op})
        elif type == 2:
            author_list.append({"name": item["name"], "op": op})
        elif type == 3:
            institution_list.append({"name": item["name"], "op": op})
        elif type == 4:
            concept_list.append({"name": item["name"], "op": op})
    institution_name = ""
    author_name = ""
    concept_name = ""
    title_name = ""
    url_institution = ""
    url_author = ""
    url_concept = ""
    if institution_list:
        for item in institution_list:
            if item["op"] == 1:
                institution_name += "(\"" + item["name"] + "\")" + " OR "
            elif item["op"] == 0:
                institution_name += "(NOT " + "\"" + item["name"] + "\")" + " OR "
        institution_name = ' '.join(institution_name.split()[:-1])
        url_institution = base_url + "institutions?filter=display_name.search:" + institution_name + "&select=id&per-page=50"
        print(url_institution)
        data_institution = requests.get(url_institution).json()
        institution_list = data_institution["results"]
        url_institution = ",institution.id:"
        for item in institution_list:
            index_of_last_slash = item["id"].rfind('/')
            institution_id = item["id"][index_of_last_slash + 1:]
            url_institution += institution_id + "|"
        url_institution = url_institution[:-1]

    if author_list:
        for item in author_list:
            if item["op"] == 1:
                author_name += "(\"" + item["name"] + "\")" + " OR "
            elif item["op"] == 0:
                author_name += "(NOT " + "\"" + item["name"] + "\")" + " OR "
        author_name = ' '.join(author_name.split()[:-1])
        url_author = base_url + "authors?filter=display_name.search:" + author_name + "&select=id&per-page=50"
        print(url_author)
        data_author = requests.get(url_author).json()
        author_list = data_author["results"]
        url_author = ",authorships.author.id:"
        for item in author_list:
            index_of_last_slash = item["id"].rfind('/')
            author_id = item["id"][index_of_last_slash + 1:]
            url_author += author_id + "|"
        url_author = url_author[:-1]

    if concept_list:
        for item in concept_list:
            if item["op"] == 1:
                concept_name += "(\"" + item["name"] + "\")" + " OR "
            elif item["op"] == 0:
                concept_name += "(NOT " + "\"" + item["name"] + "\")" + " OR "
        concept_name = ' '.join(concept_name.split()[:-1])
        url_concept = base_url + "concepts?filter=display_name.search:" + concept_name + "&select=id&per-page=3"
        data_concept = requests.get(url_concept).json()
        concept_list = data_concept["results"]
        url_concept = ",concept.id:"
        for index, item in enumerate(concept_list):
            index_of_last_slash = item["id"].rfind('/')
            concept_id = item["id"][index_of_last_slash + 1:]
            url_concept += concept_id + "|"
        url_concept = url_concept[:-1]

    if title_list:
        for item in title_list:
            if item["op"] == 1:
                title_name += "(\"" + item["name"] + "\")" + " OR "
            elif item["op"] == 0:
                title_name += "(NOT " + "\"" + item["name"] + "\")" + " OR "
        title_name = ' '.join(title_name.split()[:-1])
    # tasks = [fetch_data(url_institution), fetch_data(url_author), fetch_data(url_concept)]
    # data1, data2, data3 = await asyncio.gather(*tasks)
    # 拼接url进行搜索
    url = base_url + "works?filter=title.search:" + title_name
    if url_institution:
        url += url_institution
    if url_author:
        url += url_author
    if url_concept:
        url += url_concept
    url += ",publication_year:>" + str(min_year - 1) + ",publication_year:<" + str(max_year + 1)
    print(url)
    result_list = getWorkDetails(url)
    return JsonResponse({'data': result_list, 'error': 0})


# async def fetch_data(url):
#     async with aiohttp.ClientSession() as client:
#         async with client.get(url) as response:
#             return await response.json()


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


# 封装的函数，获取文献的详细内容
@csrf_exempt
def getWorkDetails(url):
    data = requests.get(url).json()
    result_list = []  # 用于存储结果的新列表
    for item in data["results"]:
        organization = []
        authors = []
        words = []
        work_id = []
        source = []
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

    return result_list


@csrf_exempt
async def AdvancedSearchWork1(request):  # op = 0是非 ,op=1  #type:1、2、3、4对应title、author、机构、概念
    print(1)
    search = request.POST.get("search")
    search_list = search["search_list"]
    min_year = search["min_year"]
    max_year = search["max_year"]
    title_list = []
    concept_list = []
    institution_list = []
    author_list = []
    for item in search_list:
        type = item["type"]
        op = item["op"]
        if type == 1:
            title_list.append({"name": item["name"], "op": op})
        elif type == 2:
            author_list.append({"name": item["name"], "op": op})
        elif type == 3:
            institution_list.append({"name": item["name"], "op": op})
        elif type == 4:
            concept_list.append({"name": item["name"], "op": op})
    institution_name = ""
    author_name = ""
    concept_name = ""
    title_name = ""
    url_institution = ""
    url_author = ""
    url_concept = ""

    if institution_list:
        for item in institution_list:
            if item["op"] == 1:
                institution_name += "(\"" + item["name"] + "\")" + " OR "
            elif item["op"] == 0:
                institution_name += "(NOT " + "\"" + item["name"] + "\")" + " OR "
        institution_name = ' '.join(institution_name.split()[:-1])
        url_institution = base_url + "institutions?filter=display_name.search:" + institution_name + "&select=id&per-page=50"
    if author_list:
        for item in author_list:
            if item["op"] == 1:
                author_name += "(\"" + item["name"] + "\")" + " OR "
            elif item["op"] == 0:
                author_name += "(NOT " + "\"" + item["name"] + "\")" + " OR "
        author_name = ' '.join(author_name.split()[:-1])
        url_author = base_url + "authors?filter=display_name.search:" + author_name + "&select=id&per-page=50"
    if concept_list:
        for item in concept_list:
            if item["op"] == 1:
                concept_name += "(\"" + item["name"] + "\")" + " OR "
            elif item["op"] == 0:
                concept_name += "(NOT " + "\"" + item["name"] + "\")" + " OR "
        concept_name = ' '.join(concept_name.split()[:-1])
        url_concept = base_url + "concepts?filter=display_name.search:" + concept_name + "&select=id&per-page=3"
    if title_list:
        for item in title_list:
            if item["op"] == 1:
                title_name += "(\"" + item["name"] + "\")" + " OR "
            elif item["op"] == 0:
                title_name += "(NOT " + "\"" + item["name"] + "\")" + " OR "
        title_name = ' '.join(title_name.split()[:-1])

    data_institution, data_author, data_concept = await asyncio.gather(
        fetch_data(url_institution),
        fetch_data(url_author),
        fetch_data(url_concept)
    )
    # 处理数据可能为 None 的情况
    # if data_institution is None:
    #     data_institution = {}
    # if data_author is None:
    #     data_author = {}
    # if data_concept is None:
    #     data_concept = {}

    if data_institution:
        institution_list = data_institution["results"]
        url_institution = ",institution.id:"
        for item in institution_list:
            index_of_last_slash = item["id"].rfind('/')
            institution_id = item["id"][index_of_last_slash + 1:]
            url_institution += institution_id + "|"
        url_institution = url_institution[:-1]
    if data_author:
        author_list = data_author["results"]
        url_author = ",authorships.author.id:"
        for item in author_list:
            index_of_last_slash = item["id"].rfind('/')
            author_id = item["id"][index_of_last_slash + 1:]
            url_author += author_id + "|"
        url_author = url_author[:-1]
    if data_concept:
        concept_list = data_concept["results"]
        url_concept = ",concept.id:"
        for index, item in enumerate(concept_list):
            index_of_last_slash = item["id"].rfind('/')
            concept_id = item["id"][index_of_last_slash + 1:]
            url_concept += concept_id + "|"
        url_concept = url_concept[:-1]

    # 拼接url进行搜索
    url = base_url + "works?filter=title.search:" + title_name
    if url_institution:
        url += url_institution
    if url_author:
        url += url_author
    if url_concept:
        url += url_concept
    url += ",publication_year:>" + str(min_year - 1) + ",publication_year:<" + str(max_year + 1)
    print(url)
    result_list = getWorkDetails(url)
    return JsonResponse({'data': result_list, 'error': 0})


async def fetch_data(url):
    async with aiohttp.ClientSession() as client:
        try:
            async with client.get(url) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            return None
