import requests
import json
from pprint import pprint
import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch import helpers
# url = 'http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json?key=a95b62f74f9c35f0a79ffd76ae0f927a&targetDt=20120101'
url = 'http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json'
#키값, 40개씩 나열, 2019년 개봉

queryParams = '?' + 'key=' + 'a95b62f74f9c35f0a79ffd76ae0f927a'+ '&itemPerPage=' + '300' \
            + '&openStartDt=' + '2017' + '&openEndDt=' + '2018'
url = url + queryParams

res = requests.get(url)
text = res.text


movie_list = json.loads(text)
pprint(movie_list)
movie_data = []
i=0
# movie_info = OrderedDict()
# movie = [] #csv형식으로 저장
for d in movie_list['movieListResult']['movieList']:
    # print(movie_data['openDt'], movie_data['movieNm'], movie_data['movieNmEn'],
    #       movie_data['typeNm'], movie_data['nationAlt'], movie_data['repGenreNm'], movie_data['directors'])
    #이름, 영어이름, 제작 연도, 개봉 연도, 유형, 제작 국가,
    movie_data.append({
        "_id" : i,
        "openDt" : d['openDt'],
        "movieNm" : d['movieNm'],
        "movieEn" : d['movieNmEn'],
        "typeNm" : d['typeNm'],
        "nationAlt" : d['nationAlt'],
        "repGenreNm" : d['repGenreNm'],
        "directors": d['directors']
    })
    if movie_data[i]['directors'] != list():
        movie_data[i]['directors'] = d['directors'][0]['peopleNm']
        i += 1
    else:
        movie_data[i]['directors'] = [None]
        i += 1
        continue

print(len(movie_data))
index_name = 'movie_info'
es = Elasticsearch(['localhost'],port=9200)
helpers.bulk(es, movie_data, index=index_name)

# csv형식으로 저장
data = pd.DataFrame(movie_data)
data.to_csv("movie1.csv", mode='w', encoding='ms949', index=False)