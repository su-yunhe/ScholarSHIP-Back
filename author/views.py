import traceback
import urllib.parse

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import math
# from elasticsearch import Elasticsearch

# es_url = "https://10.192.80.18:9200"
# username = "elastic"
# password = "t18*OQYzUczOZZwMP=fI"
#
# es = Elasticsearch([es_url], verify_certs=False, http_auth=(username, password))

# @csrf_exempt
# def get_scholar(request):
#     if request.method == 'POST':
#         scholar_id = request.POST.get('scholarID')
#         user_id = request.POST.get('userID')
#         es = Elasticsearch([{'host': '', 'port': 9200}], request_timeout=3600)
#         if scholar_id is None:
#             return JsonResponse({'error': 2001, 'msg': '学者ID上传失败'})
#
#         dsl = {
#             "query": {
#                 "match": {
#                     "id": scholar_id
#                 }
#             }
#         }
#         result = es.search(index='authors', body=dsl)
#         print(result)
#         if result['hits']['total'] == 0:
#             return JsonResponse({'error': 2001, 'msg': '学者ID不存在'})
#
#         scholar = result['hits']['hits']['_source']  # 待确认？
#         # 防止key error
#         if 'name' not in scholar.keys():
#             scholar['name'] = ""
#         #
#         if 'h_index' not in scholar.keys():
#             scholar['h_index'] = ""
#         # 被引用数
#         if 'n_citation' not in scholar.keys():
#             scholar['n_citation'] = ""
#         # 所属机构
#         if 'orgs' not in scholar.keys():
#             scholar['orgs'] = ""
#
#         name = scholar['name']
#         institution = scholar['orgs']
#         # papers = scholar['n_pubs']
#         citations = scholar['n_citation']
#         h_index = scholar['h_index']
#
#         if 'pubs' not in scholar.keys():
#             ps = []
#         else:
#             ps = scholar['pubs']
#         papers = []
#         # ?
#         for i in ps:
#             if 'i' not in i.keys():
#                 continue
#             papers.append(i["i"])  # ?
#         print(papers)
#
#         dsl = {
#             "query": {
#                 "terms": {
#                     "id": papers
#                 }
#             },
#             "track_total_hits": True
#         }
#         result = es.search(index='papers', body=dsl)
#         papers = result['hits']['total']['value']  # 待确认？
#         return JsonResponse({
#             'error': 0,
#             'msg': 'success',
#             'name': name,
#             'institution': institution,
#             'papers': papers,
#             'citation': citations,
#             'hIndex': h_index,
#         })
#     else:
#         return JsonResponse({'error': 1001, 'msg': "请求方式错误"})

@csrf_exempt
def get_scholar(request):
    if request.method == 'POST':
        print(request.POST)
        scholar_id = request.POST.get('scholarID')
        user_id = request.POST.get('userID')
        print(scholar_id)
        api_url = f"https://api.openalex.org/authors/{scholar_id}"
        response = requests.get(api_url)
        if response.status_code == 200:
            author = response.json()
            author_id = author['id']
            orcid = author['orcid']
            name = author['display_name']
            institution_name = author['last_known_institution']['display_name']
            citations = author['cited_by_count']
            h_index = author['summary_stats']['h_index']

            return JsonResponse({
                    'error': 0,
                    'msg': 'success',
                    'data': {
                        'scholar_id': scholar_id,
                        'name': name,
                        'institution': institution_name,
                        'essayNum': 0,
                        'citation': citations,
                        'hIndex': h_index,
                    }
                })
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return JsonResponse({'error': response.text, 'msg': "调用openAlex接口失败"})
    else:
        return JsonResponse({'error': 1001, 'msg': "请求方式错误"})

@csrf_exempt
def get_scholar_institutions(request):
    if request.method == 'POST':
        print(request.POST)
        scholar_id = request.POST.get('scholarID')
        user_id = request.POST.get('userID')
        print(scholar_id)
        api_url = f"https://api.openalex.org/authors/{scholar_id}"
        response = requests.get(api_url)
        if response.status_code == 200:
            author = response.json()
            institutions = []
            for affiliation in author['affiliations']:
                institutions.append({
                    "id": affiliation['institution']['id'].split('/')[-1],
                    "name": affiliation['institution']['display_name'],
                    "years": affiliation['years']
                })

            return JsonResponse({
                'error': 0,
                'msg': 'success',
                'institutions': institutions,
            })
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return JsonResponse({'error': response.text, 'msg': "调用openAlex接口失败"})
    else:
        return JsonResponse({'error': 1001, 'msg': "请求方式错误"})

# @csrf_exempt
# def get_scholar_papers(request):
#     if request.method == 'POST':
#         scholar_id = request.POST.get('scholarID')
#         user_id = request.POST.get('userID')
#         sort = request.POST.get('sortBy')  # default:推荐排序，time:发表时间排序，citation:被引用数排序，collect:收藏数排序
#         page = int(request.POST.get('page'))
#         size = int(request.POST.get('pageSize'))
#         es = Elasticsearch([{'host': '', 'port': 9200}], request_timeout=3600)
#
#         dsl = {
#             "query": {
#                 "match": {
#                     "id": scholar_id
#                 }
#             }
#         }
#         result = es.search(index='authors', body=dsl)
#         print(result)
#         if result['hits']['total'] == 0:
#             return JsonResponse({'error': 2001, 'msg': '学者ID不存在'})
#
#         scholar = result['hits']['hits']['_source']  # 待确认？
#         if 'pubs' not in scholar.keys():
#             ps = []
#         else:
#             ps = scholar['pubs']
#         papers = []
#         for i in ps:
#             if 'i' not in i.keys():
#                 continue
#             papers.append(i['i'])
#         print(papers)
#         # 对该学者的所有paper进行查询，并排序
#         dsl = {
#             "query": {
#                 "terms": {
#                     "id": papers
#                 }
#             },
#             "track_total_hits": True,
#             "from": (page - 1) * size,
#             "size": size,
#         }
#         if sort == '1':
#             dsl["sort"] = [{
#                 "year": "desc"
#             }]
#         elif sort == '2':
#             dsl["sort"] = [{
#                 "n_citation": "desc"
#             }]
#         else:
#             return JsonResponse({'error': 2001, 'msg': '排序方式字段不匹配！'})
#         result = es.search(index='papers', body=dsl)
#         papers = result['hits']['hits']['_source']  # 待确认？
#         num = result["hits"]["total"]["value"]
#         json_list = []
#         for paper in papers:
#             paper_id = paper['id']
#
#             # 防止key error
#             if 'authors' in paper.keys():
#                 authors = paper['authors']
#             else:
#                 authors = ""
#             if 'venue' in paper.keys():
#                 venue = paper['venue']
#             else:
#                 venue = ""
#             if 'year' in paper.keys():
#                 year = paper['year']
#             else:
#                 year = 0
#             if 'title' in paper.keys():
#                 title = paper['title']
#             else:
#                 title = ""
#             if 'n_citation' in paper.keys():
#                 n_citation = paper['n_citation']
#             else:
#                 n_citation = 0
#             if 'url' in paper.keys():
#                 url = paper['url']
#             else:
#                 url = ""
#             if 'abstract' in paper.keys():
#                 abstract = paper['abstract']
#             else:
#                 abstract = ""
#             if 'keywords' in paper.keys():
#                 keywords = paper['keywords']
#             else:
#                 keywords = ""
#             if 'doi' in paper.keys():
#                 doi = paper['doi']
#             else:
#                 doi = ""
#             json_list.append({
#                 'Title': title,
#                 'Authors': authors,
#                 'Abstract': abstract,
#                 'KeyWords': keywords,
#                 'link': url,
#                 'cites': n_citation,
#                 'publishTime': year,
#                 'id': paper_id,
#             })
#
#         return JsonResponse(
#             {'error': 0, 'msg': '查询成功', 'Num': num, 'papers': json_list})
#     else:
#         return JsonResponse({'error': 1001, 'msg': "请求方式错误"})

@csrf_exempt
def get_scholar_papers(request):
    if request.method == 'POST':
        scholar_id = request.POST.get('scholarID')
        user_id = request.POST.get('userID')
        api_url = f"https://api.openalex.org/authors/{scholar_id}"
        response = requests.get(api_url)
        if response.status_code == 200:
            author = response.json()
            works_api_url1 = author['works_api_url']
            response = requests.get(works_api_url1)

            if response.status_code == 200:
                data = response.json()
                num = data['meta']['count']
                per_page = data['meta']['per_page']
                page = math.ceil(num / per_page)  # 向上取整
                works = []
                for i in range(1, page + 1):
                    works_api_url = works_api_url1 + f'&per-page=25&page={i}'
                    print(works_api_url)
                    response = requests.get(works_api_url)
                    data = response.json()
                    ws = data['results']
                    for work in ws:
                        id = work['id'].split('/')[-1]
                        title = work['title']
                        year = work['publication_year']
                        citation = work['cited_by_count']
                        doi = str(work['doi']).split('//')[-1].split('/', 1)[-1]
                        if not work['primary_location'] is None:
                            url = work['primary_location']['landing_page_url']
                            pdf_url = work['primary_location']['pdf_url']
                        else:
                            url = ''
                            pdf_url = ''
                        # url = work['primary_location']['landing_page_url']
                        # pdf_url = work['primary_location']['pdf_url']
                        authors = []
                        for author in work['authorships']:
                            author_position = author['author_position']
                            author_id = author['author']['id'].split('/')[-1]
                            author_name = author['author']['display_name']
                            authors.append({
                                'author_position': author_position,
                                'author_id': author_id,
                                'author_name': author_name,
                            })
                        abstract = ''
                        keywords = work['keywords']
                        works.append({
                            'id': id,
                            'title': title,
                            'year': year,
                            'citation': citation,
                            'doi': doi,
                            'url': url,
                            'pdf_url': pdf_url,
                            'authors': authors,
                            'abstract': abstract,
                            'keywords': keywords
                        })
                return JsonResponse(
                    {
                        'error': 0,
                        'msg': '查询成功',
                        'Num': num,
                        'papers': works
                    })
            else:
                # 处理错误
                print(f"Error: {response.status_code} - {response.text}")
                return JsonResponse({'error': response.text, 'msg': "调用openAlex接口失败2"})
        else:
            # 处理错误
            print(f"Error: {response.status_code} - {response.text}")
            return JsonResponse({'error': response.text, 'msg': "调用openAlex接口失败1"})
    else:
        return JsonResponse({'error': 1001, 'msg': "请求方式错误"})
