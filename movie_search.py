from elasticsearch import Elasticsearch, helpers
import calendar
from pprint import pprint
es = Elasticsearch()
# movie_list_one = es.search(index='movie_list_info')

class search_response():
    def __init__(self):
        pass
    #이름으로 검색
    def movie_name_dsl(found_search):
        f = found_search
        find_data = es.search(index="movie_info",
                              filter_path=['hits.hits._source'],
                              body= {
                                  'query' : {
                                      'match' : {
                                          'movieNm' : f
                                     }
                                  }
                              })
        find_data_list = list(find_data['hits']['hits'])
        find_data_dict = find_data_list[0]['_source']

        return find_data_dict
    #연도로 검색 (영화명만 반환)
    def movie_release_dsl(found_dt):
        f_dt = found_dt #2017
        search = []
        for month in range(12):
            month += 1
            total_days = calendar.monthlen(int(f_dt), month)
            if month < 10:
                month = "0" + str(month)
            for days in range(total_days):
                if days < 10:
                    days = "0" + str(days)
                f_opendt = str(f_dt) + str(month) + str(days)
                find_data = es.search(index="movie_info",
                                    body={
                                        'query': {
                                            'match': {
                                                'openDt': f_opendt
                                            }
                                        }
                                    })

                if list(find_data['hits']['hits']) != []:
                    find_data_list = list(find_data['hits']['hits'])
                    find_data_dict = find_data_list[0]['_source']

                    search.append(find_data_dict['movieNm'])
        pprint(search)
        # print(type(search))
        return search
    def Nounsearch(found_n):
        f_n = found_n
        find_data = es.search(index="movie_senti_anal",
                              body={
                                  'query': {
                                      'match': {
                                          'review': f_n
                                      }
                                  }
                              })

        find_data_list = list(find_data['hits']['hits'])
        find_data_dict = find_data_list[0]['_source']

        return find_data_dict

    def scoresearch(score):
        num = score
        find_data = es.search(index="movie-senti-anal",
                              body={
                                  'query':{
                                      'match':{
                                          'pos_neg' : num
                                      }
                                  }
                              })

        find_data_list = list(find_data['review'])
        find_data_dict = find_data_list[0]['_source']

        return find_data_dict

    if __name__=='__main__':

        movie_name_dsl("여고괴담")
        # movie_release_dsl(2017)
