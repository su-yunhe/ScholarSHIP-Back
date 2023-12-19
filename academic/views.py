import json

import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Ban


@csrf_exempt
@require_http_methods(['GET'])
def get_works(request):
    author_id = request.GET.get('author_id')
    status = request.GET.get('status')
    response = requests.get(f'https://api.openalex.org/works?filter=authorships.author.id:{author_id}&select=authorships,cited_by_count,display_name,doi,id,institutions_distinct_count,language,publication_date')
    articles = response.json().get('results')
    unbanned_articles = []
    banned_articles = []
    for article in articles:
        authors = []
        institutions = []
        for author in article.get('authorships'):
            authors.append(author.get('author'))
            for i in author.get('institutions'):
                i = {"id": i.get('id'), "display_name": i.get('display_name')}
                if i not in institutions:
                    institutions.append(i)
        article["authors"] = authors
        article["institutions"] = institutions
        article.pop("authorships")

        if Ban.objects.filter(work_id=article.get('id').split('/')[-1]).exists():
            banned_articles.append(article)
        else:
            unbanned_articles.append(article)

    return_articles = unbanned_articles if status == "true" else banned_articles
    return JsonResponse({"articles": return_articles})


@csrf_exempt
@require_http_methods(['GET'])
def get_detail(request):
    work_id = request.GET.get('work_id')
    user_id = request.GET.get('user_id')
    ban_info = Ban.objects.filter(work_id=work_id)

    if ban_info.exists():
        if user_id not in ban_info.first().author_id:
            return JsonResponse({"err": "未找到论文"})

    response = requests.get(f'https://api.openalex.org/{work_id}/?select=abstract_inverted_index,authorships,cited_by_count,concepts,counts_by_year,display_name,title,doi,id,institutions_distinct_count,language,primary_location,publication_date,referenced_works,related_works,type')
    article = response.json()

    authors = []
    institutions = []
    for author in article.get('authorships'):
        authors.append({"author_position": author.get('author_position'), "author": author.get('author')})
        for i in author.get('institutions'):
            i = {"id": i.get('id'), "display_name": i.get('display_name')}
            if i not in institutions:
                institutions.append(i)
    article["authorships"] = authors
    article["institutions"] = institutions
    article["concepts"] = [{"display_name": concept.get('display_name'), "score": concept.get('score')} for concept in article.get('concepts')]

    abstract_words = article.get('abstract_inverted_index')
    if abstract_words is not None:
        abstract = []
        for word in abstract_words:
            for num in abstract_words.get(word):
                abstract.insert(num, word)
        article["abstract"] = ' '.join(abstract)
        article.pop('abstract_inverted_index')

    return JsonResponse({"result": article})


@csrf_exempt
@require_http_methods(['POST'])
def change_status(request):
    work_id = json.loads(request.body).get('work_id')

    if Ban.objects.filter(work_id=work_id).exists():
        Ban.objects.get(work_id=work_id).delete()
    else:
        response = requests.get(f'https://api.openalex.org/{work_id}/?select=authorships')
        authors = response.json().get("authorships")
        authors = [author.get("author").get("id").split('/')[-1] for author in authors]
        Ban.objects.create(work_id=work_id, author_id=authors)

    return JsonResponse({"err": 0})


@csrf_exempt
@require_http_methods(['GET'])
def get_relation_map(request):
    root_id = request.GET.get('root_id')
    print(root_id)
    result_json = get_relation(root_id)

    return JsonResponse(result_json)


def get_relation(root_id):
    response = requests.get(f'https://api.openalex.org/works?filter=authorships.author.id:{root_id}&select=title,authorships&sort=cited_by_count')
    data = response.json()
    results = data.get('results', [])
    # print(results)
    if not results:
        return None
    results = results[:5]
    result_authors = []
    result_lines = []
    for result in results:
        article_name = result.get('title')
        authorships = result.get('authorships')
        # 获取所有的 "author"
        authors = [{"id": authorship.get('author').get('id').split('/')[-1], "name": authorship.get('author').get('display_name')} for authorship in authorships]
        for i in range(len(authors)):
            author = authors[i]
            for j in range(i + 1, len(authors)):
                to_author = authors[j]
                result_lines.append({
                    "from": author.get('id'),
                    "to": to_author.get('id'),
                    "article": article_name,
                })
            if author not in result_authors:
                result_authors.append({
                    "id": author.get('id'),
                    "name": author.get('name')
                })

    return {'root_id': root_id, 'nodes': result_authors, 'lines': result_lines}
