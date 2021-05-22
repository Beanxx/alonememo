from flask import Flask
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = None

# 플라스트 동작시킬 때 create_app() 함수의 결과로 리턴

def create_app(database_name='sparta'):
    # 플라스크 웹 서버 생성하기
    app = Flask(__name__)
    app.debug = True
    app.config.from_pyfile('config.py')

    global db
    db = client.get_database(database_name)

    # 순환 참조 방지
    from app.views import api, main, memo, user

    app.register_blueprint(api.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(memo.bp)
    app.register_blueprint(user.bp)

    return app