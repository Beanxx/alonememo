from flask import Flask
from pymongo import MongoClient

# mongodb 추가
client = MongoClient('localhost', 27017)
db = None

# 플라스트 프레임워크에서 지정한 함수 이름
# 플라스트 동작시킬 때 create_app() 함수의 결과로 리턴

def create_app(database_name='sparta'):  # default 값으로 'sparta'를 쓰겠다.
    # 플라스크 웹 서버 생성하기
    app = Flask(__name__)
    app.debug = True
    app.config.from_pyfile('config.py')

    # 파이썬 중급 - 전역 변수를 함수 내부에서 수정 가능하게 만들어줌
    global db
    db = client.get_database(database_name)

    # 순환 참조 방지
    from app.views import api, main, memo, user

    app.register_blueprint(api.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(memo.bp)
    app.register_blueprint(user.bp)

    return app