from konlpy.tag import Okt
import json
import os
from pprint import pprint
import nltk
import numpy as np
from keras import models, layers, optimizers, losses, metrics
import matplotlib.pyplot as plt
from elasticsearch import Elasticsearch, helpers
plt.rcParams['font.family'] = 'Malgun Gothic'


def read_data(filename):
    with open(filename, 'r', encoding='UTF8') as f:
        data = [line.split('\t') for line in f.read().splitlines()]
        # txt 파일의 헤더(id document label)는 제외하기
        data = data[1:]
    return data

train_data = read_data('input_data/ratings_train.txt')
test_data = read_data('input_data/ratings_test.txt')

print(len(train_data))
print(len(train_data[0]))
print(len(test_data))
print(len(test_data[0]))

# 1) morphs : 형태소 추출
# 2) pos : 품사 부착(Part-of-speech tagging)
# 3) nouns : 명사 추출
okt = Okt()
print(okt.pos(u'이 밤 그날의 반딧불을 당신의 창 가까이 보낼게요'))

def tokenize(doc):
    # norm은 정규화, stem은 근어로 표시하기를 나타냄
    return ['/'.join(t) for t in okt.pos(doc, norm=True, stem=True)]

if os.path.isfile('train_docs.json'):
    with open('train_docs.json', encoding='UTF8') as f:
        train_docs = json.load(f)
    with open('test_docs.json', encoding='UTF8') as f:
        test_docs = json.load(f)
else:
    train_docs = [(tokenize(row[1]), row[2]) for row in train_data]
    test_docs = [(tokenize(row[1]), row[2]) for row in test_data]
    # JSON 파일로 저장
    with open('train_docs.json', 'w', encoding="utf-8") as make_file:
        json.dump(train_docs, make_file, ensure_ascii=False, indent="\t")
    with open('test_docs.json', 'w', encoding="utf-8") as make_file:
        json.dump(test_docs, make_file, ensure_ascii=False, indent="\t")

# 예쁘게(?) 출력하기 위해서 pprint 라이브러리 사용
pprint(train_docs[0])

tokens = [t for d in train_docs for t in d[0]]
print(len(tokens))

text = nltk.Text(tokens, name='NMSC')

# 전체 토큰의 개수
print(len(text.tokens))
# 중복을 제외한 토큰의 개수
print(len(set(text.tokens)))
# 출현 빈도가 높은 상위 토큰 10개
pprint(text.vocab().most_common(10))
# 시간이 꽤 걸립니다! 시간을 절약하고 싶으면 most_common의 매개변수를 줄여보세요.
# most_common(100) 의 수를 높일 수록 정확도가 올라갑니다.
selected_words = [f[0] for f in text.vocab().most_common(200)]

def term_frequency(doc):
    return [doc.count(word) for word in selected_words]

train_x = [term_frequency(d) for d, _ in train_docs]
test_x = [term_frequency(d) for d, _ in test_docs]
train_y = [c for _, c in train_docs]
test_y = [c for _, c in test_docs]

x_train = np.asarray(train_x).astype('float32')
x_test = np.asarray(test_x).astype('float32')
y_train = np.asarray(train_y).astype('float32')
y_test = np.asarray(test_y).astype('float32')


model = models.Sequential()
model.add(layers.Dense(256, activation='relu', input_shape=(200,)))
model.add(layers.Dense(256, activation='relu'))
model.add(layers.Dense(1, activation='sigmoid'))

model.compile(optimizer=optimizers.RMSprop(lr=0.001), loss=losses.binary_crossentropy, metrics=[metrics.binary_accuracy])

model.fit(x_train, y_train, epochs=10, batch_size=1024)
results = model.evaluate(x_test, y_test)


def predict_pos_neg(review):
    token = tokenize(review)
    tf = term_frequency(token)
    data = np.expand_dims(np.asarray(tf).astype('float32'), axis=0)
    score = float(model.predict(data))
    return score * 10
# 테스트
# predict_pos_neg("올해 최고의 영화! 세 번 넘게 봐도 질리지가 않네요.")

all_data = read_data('input_data/ratings.txt')
all_data = all_data[1:]

index_name = 'movie_senti_anal'
docs = []

for i in range(len(all_data)):
    docs.append({
        '_id' : i,
        'review':all_data[i][1],
        'pos_neg':int(predict_pos_neg(all_data[i][1]))
    })
es = Elasticsearch(['localhost'], port=9200)
helpers.bulk(es, docs, index=index_name)