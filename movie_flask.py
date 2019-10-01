# import Flask
from flask import Flask, request, make_response, jsonify
import json
from collections import OrderedDict
from movie_search import search_response
from pprint import pprint
from konlpy.tag import Okt

# flask app 초기화
app = Flask(__name__)

# 기본 route
@app.route('/')
def index():
    return 'Hello World!'

# webhook route
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # return response
    return make_response(jsonify(results()))

# 응답 함수
def results():
    # build a request object
    data = request.get_json(silent=True)
    file_data = OrderedDict()
    a = ['movieNm','movieEn','directors','nationAlt','openDt','repGenreNm','typeNm']
    data = data['queryResult']['parameters']

    if data['movieNm'] != '':
        name_info = search_response.movie_name_dsl(data['movieNm'])
        file_data["fulfillmentText"] = """영화 : {0} 영어 : {1} 감독 : {2} 국가 : {3} 개봉일 : {4}
          길이 : {5} 타입 : {6}""".format(name_info[a[0]],name_info[a[1]],name_info[a[2]]
                                      ,name_info[a[3]],name_info[a[4]],name_info[a[5]]
                                      ,name_info[a[6]])

    elif data['openDt'] != '':
        release_info = search_response.movie_release_dsl(data['openDt'])
        file_data["fulfillmentText"] = '영화 : {0}'.format(release_info)
    else:
        sentence = data['queryResult']
        sentences_tag = []
        noun_list = []
        okt = Okt()
        morph = okt.pos(sentence)
        sentences_tag.append(morph)

        for sentence1 in sentences_tag:
            for word, tag in sentence1:
                if tag in ['Noun', 'Adjective']:
                    noun_list.append(word)
        noun_info = search_response.Nounsearch(data['Noun'])
        file_data['fulfillmentText'] = noun_info


# app 실행
if __name__ == '__main__':
   app.run()
