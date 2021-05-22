# 테스트 함수는
# test_ 접두사로 시작
# client 인자는 웹브라우저 클라이언트처럼 동작
# client 인자 설정은 pytest-flask 패키지에서 작업해줌

def test_메인_페이지(client):
    response = client.get('/')

    # assert 구문을 이용해서 검증
    # htl 파일을 잘 리턴해주는지 확인
    assert response.status_code == 200


def test_없는_페이지(client):
    response = client.get('/invalid')
    assert response.status_code == 404


def test_로그인_페이지(client):
    response = client.get('/login')
    assert response.status_code == 200


def test_회원가입_페이지(client):
    response = client.get('/register')
    assert response.status_code == 200