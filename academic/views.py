import json
import random

import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


from .models import Ban, BanCount
import re
from datetime import datetime


@csrf_exempt
@require_http_methods(['GET'])
def get_works(request):
    author_id = request.GET.get('author_id')
    status = request.GET.get('status')
    count = request.GET.get('count')
    # page = 1
    # articles = []
    #
    # while True:
    #     response = requests.get(f'https://api.openalex.org/works?filter=authorships.author.id:{author_id}&per_page=50&page={page}&select=abstract_inverted_index,authorships,cited_by_count,display_name,doi,id,language,primary_location,publication_date')
    #     page += 1
    #     results = response.json().get('results')
    #     if len(results) == 0:
    #         break
    #     articles += response.json().get('results')
    # print(articles)
    response = requests.get(f'https://api.openalex.org/works?filter=authorships.author.id:{author_id}&per_page=50&page={count}&select=abstract_inverted_index,authorships,cited_by_count,display_name,doi,id,language,primary_location,publication_date')
    articles = response.json().get('results')
    unbanned_articles = []
    banned_articles = []
    for article in articles:
        # print(article.get('display_name'))
        authors = []
        for author in article.get('authorships'):
            authors.append(author.get('author'))
        article["authors"] = authors
        article.pop("authorships")

        abstract_words = article.get('abstract_inverted_index')
        if abstract_words is not None:
            abstract = []
            for word in abstract_words:
                for num in abstract_words.get(word):
                    abstract.insert(num, word)
            article["abstract"] = ' '.join(abstract)
            article.pop('abstract_inverted_index')

        # print(article.get('primary_location').get('pdf_url'))
        if article.get('primary_location') is not None:
            article["pdf_url"] = article.get('primary_location').get('pdf_url')
            article.pop("primary_location")

        if Ban.objects.filter(work_id=article.get('id').split('/')[-1]).exists():
            banned_articles.append(article)
        else:
            unbanned_articles.append(article)
    return_articles = unbanned_articles if status == "true" else banned_articles
    return JsonResponse({"error": 0, "result": return_articles})


@csrf_exempt
@require_http_methods(['GET'])
def get_works_count(request):
    author_id = request.GET.get('author_id')
    response = requests.get(f'https://api.openalex.org/authors/{author_id}/?select=works_count')
    count = response.json().get('works_count')
    if BanCount.objects.filter(author_id=author_id).exists() and count is not None:
        count -= BanCount.objects.get(author_id=author_id).ban_count
    return JsonResponse({"error": 0, "result": {"works_count": count}})


@csrf_exempt
@require_http_methods(['GET'])
def get_detail(request):
    work_id = request.GET.get('work_id')
    user_id = request.GET.get('user_id')
    ban_info = Ban.objects.filter(work_id=work_id)

    if ban_info.exists():
        if user_id not in ban_info.first().author_id:
            return JsonResponse({"error": 3001, "msg": "未找到论文"})

    response = requests.get(f'https://api.openalex.org/{work_id}/?select=abstract_inverted_index,authorships,cited_by_count,concepts,counts_by_year,display_name,title,doi,id,institutions_distinct_count,language,primary_location,publication_date,type')
    article = response.json()

    authors = []
    for author in article.get('authorships'):
        authors.append({"author_position": author.get('author_position'), "author": author.get('author')})

    i = article.get('authorships')[0].get('institutions')[0]
    institution = {"id": i.get('id'), "display_name": i.get('display_name')}

    article["authorships"] = authors
    article["institution"] = institution
    article["concepts"] = [{"display_name": concept.get('display_name'), "score": concept.get('score')} for concept in article.get('concepts')]

    abstract_words = article.get('abstract_inverted_index')
    if abstract_words is not None:
        abstract = []
        for word in abstract_words:
            for num in abstract_words.get(word):
                abstract.insert(num, word)
        article["abstract"] = ' '.join(abstract)
        article.pop('abstract_inverted_index')

    return JsonResponse({"error": 0, "result": article})
# @csrf_exempt
# @require_http_methods(['GET'])
# def get_detail(request):
#     work_id = request.GET.get('work_id')
#     user_id = request.GET.get('user_id')
#     ban_info = Ban.objects.filter(work_id=work_id)
#
#     if ban_info.exists():
#         if user_id not in ban_info.first().author_id:
#             return JsonResponse({"error": 3001, "msg": 未找到论文"})
#
#     response = requests.get(f'https://api.openalex.org/{work_id}/?select=abstract_inverted_index,authorships,cited_by_count,concepts,counts_by_year,display_name,title,doi,id,institutions_distinct_count,language,primary_location,publication_date,referenced_works,related_works,type')
#     article = response.json()
#
#     authors = []
#     institutions = []
#     for author in article.get('authorships'):
#         authors.append({"author_position": author.get('author_position'), "author": author.get('author')})
#         for i in author.get('institutions'):
#             i = {"id": i.get('id'), "display_name": i.get('display_name')}
#             if i not in institutions:
#                 institutions.append(i)
#     article["authorships"] = authors
#     article["institutions"] = institutions
#     article["concepts"] = [{"display_name": concept.get('display_name'), "score": concept.get('score')} for concept in article.get('concepts')]
#
#     abstract_words = article.get('abstract_inverted_index')
#     if abstract_words is not None:
#         abstract = []
#         for word in abstract_words:
#             for num in abstract_words.get(word):
#                 abstract.insert(num, word)
#         article["abstract"] = ' '.join(abstract)
#         article.pop('abstract_inverted_index')
#
#     return JsonResponse({"error": 0, "result": article})


@csrf_exempt
@require_http_methods(['GET'])
def get_referenced_related(request):
    work_id = request.GET.get('work_id')
    user_id = request.GET.get('user_id')
    ban_info = Ban.objects.filter(work_id=work_id)

    if ban_info.exists():
        if user_id not in ban_info.first().author_id:
            return JsonResponse({"error": 3001, "msg": "未找到论文"})

    response = requests.get(f'https://api.openalex.org/{work_id}/?select=referenced_works,related_works,doi')
    article = response.json()
    referenced = []
    for ref in article.get('referenced_works'):
        ref = ref.split('/')[-1]
        response = requests.get(f'https://api.openalex.org/{ref}/?select=title')
        data = response.json()
        if data.get('title') != "Deleted Work":
            referenced.append({"id": ref, "title": data.get('title')})
    article["referenced_works"] = referenced

    related = []
    for rel in article.get('related_works'):
        rel = rel.split('/')[-1]
        response = requests.get(f'https://api.openalex.org/{rel}/?select=title')
        data = response.json()
        if data.get('title') != "Deleted Work":
            related.append({"id": rel, "title": data.get('title')})
    article["related_works"] = related
    return JsonResponse({"error": 0, "result": article})


@csrf_exempt
@require_http_methods(['GET'])
def get_referenced_related(request):
    work_id = request.GET.get('work_id')
    user_id = request.GET.get('user_id')
    ban_info = Ban.objects.filter(work_id=work_id)

    if ban_info.exists():
        if user_id not in ban_info.first().author_id:
            return JsonResponse({"error": 3001, "msg": "未找到论文"})

    referenced = requests.get(f'https://api.openalex.org/works?filter=cited_by:{work_id}&select=id,title').json().get("results")
    related = requests.get(f'https://api.openalex.org/works?filter=related_to:{work_id}&select=id,title').json().get("results")

    article = {}
    referenced_results = []
    for ref in referenced:
        if ref.get('title') != "Deleted Work":
            referenced_results.append({"id": ref.get("id").split("/")[-1], "title": ref.get('title')})
    article["referenced_works"] = referenced

    related_results = []
    for rel in related:
        if rel.get('title') != "Deleted Work":
            related_results.append({"id": rel.get("id").split("/")[-1], "title": rel.get('title')})
    article["related_works"] = related
    return JsonResponse({"error": 0, "result": article})


@csrf_exempt
@require_http_methods(['POST'])
def change_status(request):
    # work_id = json.loads(request.body).get('work_id')
    work_id = request.POST.get("work_id")
    if Ban.objects.filter(work_id=work_id).exists():
        ban = Ban.objects.get(work_id=work_id)
        for author in ban.author_id:
            banCount = BanCount.objects.get(author_id=author)
            banCount.ban_count -= 1
            banCount.save()
            if banCount.ban_count == 0:
                banCount.delete()
        ban.delete()
    else:
        response = requests.get(f'https://api.openalex.org/{work_id}/?select=authorships')
        authors = response.json().get("authorships")
        authors = [author.get("author").get("id").split('/')[-1] for author in authors]
        Ban.objects.create(work_id=work_id, author_id=authors)
        for author in authors:
            if BanCount.objects.filter(author_id=author).exists():
                bc = BanCount.objects.get(author_id=author)
                bc.ban_count += 1
                bc.save()
            else:
                BanCount.objects.create(author_id=author)

    return JsonResponse({"error": 0})


@csrf_exempt
@require_http_methods(['GET'])
def get_relation_map(request):
    root_id = request.GET.get('root_id')
    result_json = get_relation(root_id)

    return JsonResponse({"error": 0, "result": result_json})


def get_relation(root_id):
    response = requests.get(f'https://api.openalex.org/works?filter=authorships.author.id:{root_id}&select=title,authorships&sort=cited_by_count')
    data = response.json()
    results = data.get('results', [])
    if not results:
        return None
    results = results[:5]
    result_authors = []
    result_lines = []
    limit = 25
    for result in results:
        article_name = result.get('title')
        authorships = result.get('authorships')
        # 获取所有的 "author"
        authors = [{"id": authorship.get('author').get('id').split('/')[-1], "name": authorship.get('author').get('display_name')} for authorship in authorships]
        # print(len(result_authors))
        # print(len(authors))
        if len(result_authors) + len(authors) > limit:
            continue
        for i in range(len(authors)):
            author = authors[i]
            for j in range(i + 1, len(authors)):
                inRes = False
                to_author = authors[j]
                for lin in result_lines:
                    if (lin.get("from") == author.get('id') and lin.get("to") == to_author.get('id')) or (lin.get("from") == to_author.get('id') and lin.get("to") == author.get('id')):
                        inRes = True
                        break
                if inRes:
                    continue
                result_lines.append({
                    "from": author.get('id'),
                    "to": to_author.get('id'),
                    "text": "合著",
                    "article": article_name,
                })
            author_json = {
                    "id": author.get('id'),
                    "text": author.get('name')
                }
            if author_json not in result_authors:
                result_authors.append(author_json)

    return {'root_id': root_id, 'nodes': result_authors, 'lines': result_lines}


def generate_ieee_citation(paper_data):
    authorships = paper_data.get('authorships')

    authors = [authorship.get('author').get('display_name') for authorship in authorships]

    title = paper_data.get('title')

    formatted_authors = []

    for author in authors:
        names = author.split(' ')
        first_names = ' '.join(names[:-1])
        last_name = names[-1]

        first = ''.join(char for char in first_names if (char.isupper() or char == ' ' or char == '-'))

        formatted_name = first + ' ' + last_name
        formatted_name = formatted_name.replace(' ', '. ')
        formatted_authors.append(formatted_name)

    if len(authors) == 1:
        authors = formatted_authors[0]
    elif len(authors) == 2:
        authors = ', and '.join(formatted_authors)
    elif len(authors) == 3:
        authors = formatted_authors[0] + ', ' + formatted_authors[1] + ', and ' + formatted_authors[2]
    else:
        authors = formatted_authors[0] + ' et al.'

    source = paper_data.get('primary_location').get('source').get('display_name')

    publication_date = paper_data.get('publication_date')

    date_object = datetime.strptime(publication_date, "%Y-%m-%d")

    formatted_date = date_object.strftime("%b. %Y")

    doi = paper_data.get('doi').split("doi.org/")[-1]

    # 生成 IEEE 引用格式
    ieee_citation = f"{authors}, \"{title},\" {source}, {formatted_date}. doi: {doi}."

    return ieee_citation


def generate_gbt_citation(paper_data):
    authorships = paper_data.get('authorships')

    authors = [authorship.get('author').get('display_name') for authorship in authorships]

    title = paper_data.get('title')

    formatted_authors = []

    for author in authors:
        names = re.split(r'\s|-', author)

        first_names = names[:-1]
        last_name = names[-1]

        first = ' '.join(first_name[0] for first_name in first_names)

        formatted_name = last_name + ' ' + first
        formatted_authors.append(formatted_name)

    if len(authors) <= 3:
        authors = ', '.join(formatted_authors)
    else:
        authors = ', '.join(formatted_authors[:3]) + ', et al'

    source = paper_data.get('primary_location').get('source').get('display_name')

    publication_date = paper_data.get('publication_date')

    date_object = datetime.strptime(publication_date, "%Y-%m-%d")

    formatted_date = date_object.strftime("%Y")

    biblio = paper_data.get('biblio')

    volume = biblio.get('volume')
    issue = biblio.get('issue')
    first_page = biblio.get('first_page')
    last_page = biblio.get('last_page')

    # 生成 GB/T 引用格式
    gbt_citation = f"{authors}. {title}. {source}, {formatted_date}, {volume}({issue}): {first_page}-{last_page}."

    return gbt_citation


def generate_bib_citation(paper_data):

    key = ''

    authorships = paper_data.get('authorships')

    authors = [authorship.get('author').get('display_name') for authorship in authorships]

    title = paper_data.get('title')

    formatted_authors = []

    for author in authors:
        names = re.split(r'\s', author)

        first_names = names[:-1]
        last_name = names[-1]

        key += last_name + '_'

        first_name = ' '.join(first_names)

        formatted_name = last_name + ', ' + first_name
        formatted_authors.append(formatted_name)

    authors = ' and '.join(formatted_authors)

    source = paper_data.get('primary_location').get('source').get('display_name')

    publication_date = paper_data.get('publication_date')

    date_object = datetime.strptime(publication_date, "%Y-%m-%d")

    formatted_year = date_object.strftime("%Y")
    formatted_month = date_object.strftime("%b")

    key += formatted_year

    language = paper_data.get('language')

    doi = paper_data.get('doi').split("doi.org/")[-1]

    # 生成 IEEE 引用格式
    bib_citation = f"@article{{{key}, \n" + f"author={{{authors}}}, \n" + f"title={{{title}}}, \n"
    if source:
        bib_citation += f"source={{{source}}}, \n"
    if formatted_year:
        bib_citation += f"year={{{formatted_year}}}, \n"
    if formatted_month:
        bib_citation += f"month={{{formatted_month}}}, \n"
    bib_citation += f"language={{{language}}} \n}}"

    return bib_citation


def generate_chicago_citation(paper_data):
    authorships = paper_data.get('authorships')

    authors = [authorship.get('author').get('display_name') for authorship in authorships]

    title = paper_data.get('title')

    formatted_authors = []

    author = authors[0]
    names = author.split(' ')
    first_names = ' '.join(names[:-1])
    last_name = names[-1]
    author = last_name + ', ' + first_names

    formatted_authors.append(author)
    formatted_authors += authors[1:]

    if len(authors) == 1:
        authors = formatted_authors[0]
    else:
        authors = ', '.join(formatted_authors[:-1]) + ', and ' + formatted_authors[-1]

    source = paper_data.get('primary_location').get('source').get('display_name')

    publication_date = paper_data.get('publication_date')

    date_object = datetime.strptime(publication_date, "%Y-%m-%d")

    formatted_year = date_object.strftime("%Y")
    formatted_month = date_object.strftime("%B")

    biblio = paper_data.get('biblio')

    first_page = biblio.get('first_page')
    last_page = biblio.get('last_page')

    doi = paper_data.get('doi').split("doi.org/")[-1]

    # 生成 Chicago 引用格式
    chicago_citation = f"{authors}. {formatted_year}. \"{title}.\" {source}, {formatted_month}, {first_page}-{last_page}. doi: {doi}."

    return chicago_citation


@csrf_exempt
@require_http_methods(['GET'])
def get_citation(request):
    work_id = request.GET.get('work_id')
    citation_type = request.GET.get('citation_type')

    response = requests.get(f'https://api.openalex.org/{work_id}')
    paper_data = response.json()
    if citation_type == "IEEE":
        citation_result = generate_ieee_citation(paper_data)
    elif citation_type == "GB/T7714":
        citation_result = generate_gbt_citation(paper_data)
    elif citation_type == "BibText":
        citation_result = generate_bib_citation(paper_data)
    elif citation_type == "Chicago":
        citation_result = generate_chicago_citation(paper_data)
    else:
        citation_result = "type error"

    return JsonResponse({"error": 0, "result": citation_result})


