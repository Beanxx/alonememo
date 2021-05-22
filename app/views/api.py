import datetime
import hashlib

import jwt
from flask import Blueprint, request, jsonify, current_app

from app import db

bp = Blueprint(
    'api', #
    __name__,
    url_prefix='/api')


@bp.route('/register/naver', methods=['POST'])
def api_register_naver():
    naver_id = request.form['naver_id']

    if not db.users.find_one({'id': naver_id}, {'_id': False}):
        db.users.insert_one({'id': naver_id, 'pw': ''})

    # JWT 발급
    expiration_time = datetime.timedelta(hours=1)

    payload = {
        'id': naver_id,
        'exp': datetime.datetime.utcnow() + expiration_time
    }
    token = jwt.encode(payload, current_app.config['JWT_SECRET'])
    print(token)

    return jsonify({'result': 'success', 'token': token})


@bp.route('/login', methods=['POST'])
def api_login():
    id = request.form['id_give']
    pw = request.form['pw_give']

    pw_hash = hashlib.sha256(pw.encode()).hexdigest()

    user = db.users.find_one({'id': id, 'pw': pw_hash}, {'_id': False})

    # 만약 가입했다면?
    if user:
        # 로그인 성공이기 때문에 JWT 생성
        expiration_time = datetime.timedelta(hours=1)
        payload = {
            'id': id,
            # 발급시간으로부터 1시간동안 JWT 유효
            'exp': datetime.datetime.utcnow() + expiration_time
        }
        token = jwt.encode(payload, current_app.config['JWT_SECRET'])
        print(token)

        return jsonify({'result': 'success', 'token': token})
    else:
        # 가입하지 않은 상태
        return jsonify({'result': 'fail', 'msg': '로그인 실패'})


@bp.route('/register', methods=['POST'])
def api_register():
    id = request.form['id_give']
    pw = request.form['pw_give']

    # salting
    # 1. pw + 랜덤 문자열 추가(솔트)
    # 솔트 추가된 비밀번호를 해시
    # DB에 저장할 때는 (해시 결과물 + 적용한 솔트) 묶어서 저장

    # 회원가입
    pw_hash = hashlib.sha256(pw.encode()).hexdigest()
    db.users.insert_one({'id': id, 'pw': pw_hash})

    return jsonify({'result': 'success'})