import datetime
import hashlib
import os

import jwt
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

from pymongo import MongoClient

# 플라스크 웹 서버 생성하기
app = Flask(__name__)

# mongodb 추가
client = MongoClient('localhost', 27017)
db = client.get_database('sparta')

# .env 파일 읽어와 환경변수로 추가
load_dotenv()
# load_dotenv() 설정
JWT_SECRET = os.environ['JWT_SECRET']


# API 추가
@app.route('/', methods=['GET'])  # 데코레이터 문법
def index():  # 함수 이름은 고유해야 한다
    token = request.cookies.get('loginToken')

    if token:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            print(payload)
            memos = list(db.articles.find({'id': payload['id']}, {'_id': False}))
        except jwt.ExpiredSignatureError:
            memos = []
    else:
        memos = []

    return render_template('index.html', test='테스트', memos=memos)


# 로그인
@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


# 가입
@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')


# 가입 API
@app.route('/api/register', methods=['POST'])
def api_register():
    id = request.form['id_give']
    pw = request.form['pw_give']

    pw_hash = hashlib.sha256(pw.encode()).hexdigest()
    db.user.insert_one({'id': id, 'pw': pw_hash})

    return jsonify({'result': 'success'})


# 로그인 API
@app.route('/api/login', methods=['POST'])
def api_login():
    id = request.form['id_give']
    pw = request.form['pw_give']

    pw_hash = hashlib.sha256(pw.encode()).hexdigest()
    user = db.user.find_one({'id': id, 'pw': pw_hash})

    # 로그인 성공 시 JWT 리턴
    if user:
        expiration_time = datetime.timedelta(hours=1)
        payload = {
            'id': id,
            # JWT 유효 기간 - 이 시간 이후에는 JWT 인증이 불가능합니다.
            'exp': datetime.datetime.utcnow() + expiration_time,
        }
        token = jwt.encode(payload, JWT_SECRET).decode()
        return jsonify({'result': 'success', 'token': token, 'msg': '로그인 성공'})

    return jsonify({'result': 'fail', 'msg': '아이디 비밀번호 불일치'})


@app.route('/user', methods=['POST'])
def user():


    token_receive = request.headers['authorization']
    token = token_receive.split()[1]
    print(token)

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        print(payload)
        id = payload['id']
        return jsonify({'result': 'success', 'id': id})
    except jwt.exceptions.ExpiredSignatureError:
        # try 부분을 실행했지만 위와 같은 에러가 난다면
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})


# 아티클 추가 API
@app.route('/memo', methods=['POST'])
def save_memo():
    form = request.form
    url_receive = form['url_give']
    comment_receive = form['comment_give']

    print(url_receive, comment_receive)

    token_receive = request.headers['authorization']
    token = token_receive.split()[1]
    print(token)

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        print(payload)
        id = payload['id']
        return jsonify({'result': 'success', 'id': id})
    except jwt.exceptions.ExpiredSignatureError:
        # try 부분을 실행했지만 위와 같은 에러가 난다면
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})


    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}  # chrome
    response = requests.get(
        url_receive,
        headers=headers
    )
    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.select_one('meta[property="og:title"]')
    url = soup.select_one('meta[property="og:url"]')
    image = soup.select_one('meta[property="og:image"]')
    description = soup.select_one('meta[property="og:description"]')
    print(title['content'])
    print(url['content'])
    print(image['content'])
    print(description['content'])

    document = {
        'title': title['content'],
        'image': image['content'],
        'description': description['content'],
        'url': url['content'],
        'comment': comment_receive,
        'id': payload['id']
    }
    db.articles.insert_one(document)

    return jsonify(
        {'result': 'success', 'msg': '저장했습니다.'}
    )


@app.route('/memo', methods=['GET'])
def list_memo():
    memos = list(db.articles.find({}, {'_id': False}))
    result = {
        'result': 'success',
        'articles': memos,
    }

    return jsonify(result)


# app.py 파일을 직접 실행 시킬 때 동작시킴
# 이 코드가 가장 아래 위치
if __name__ == '__main__':
    app.run(
        '0.0.0.0',  # 모든 IP에서 오는 요청을 허용
        7000,  # 플라스크 웹 서버는 7000번 포트 사용 (1024보다만 크면 됨)
        debug=True,  # 에러 발생 시 에러 로그 보여줌
    )
