from flask import render_template, redirect, request, session, url_for, jsonify
from auth.models import User
from datetime import datetime
from app import db
from auth import auth
import hashlib
import re


@auth.context_processor
def today_date():
    return dict(datetime=datetime)


@auth.route('/check_id', methods=['POST'])
def check_id():
    username = request.get_json()['username']  # POST 요청으로부터 username 파라미터 추출
    if len(username) == 0:
        result = {'message': '아이디를 입력해주세요.'}
        return jsonify(result)

    available_id = checkDupId(username)
    if not available_id:
        result = {'message': '중복된 아이디입니다.'}
    else:
        result = {'message': '사용가능한 아이디입니다.'}

    return jsonify(result)
 
@auth.route('/check_form', methods=['POST'])
def check_form():
    name = request.get_json()['name']
    username = request.get_json()['username']
    password = request.get_json()['password']
    email = request.get_json()['email']

    if len(name) == 0 or len(username) == 0 or len(password) == 0 or len(email) == 0:
        result = {'error': '정확한 정보를 입력해주세요.'}
        return jsonify(result), 400

    if not checkPwLen(password):
        result = {'error': '비밀번호는 4자리 이상 설정 가능합니다.'}
        return jsonify(result), 400

    if not checkEmailForm(email):
        result = {'error': '이메일 형식이 올바르지 않습니다.'}
        return jsonify(result), 400
    
    result = {'success': '양식이 정상적으로 작성되었습니다.'}
    return jsonify(result), 200


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.get_json()['name']
        username = request.get_json()['username']
        password = request.get_json()['password']
        email = request.get_json()['email']
        birth = datetime.strptime(request.get_json()['birth'], '%Y-%m-%d')

        user = User(
            name=name, username=username, password=hash_password(password), email=email, birth=birth
        )  # User 모델 객체 생성
        db.session.add(user)  # 데이터베이스에 추가
        db.session.commit()  # 변경사항 저장
        result = {'success': '양식이 정상적으로 작성되었습니다.'}
        return jsonify(result), 200
        
    elif request.method == 'GET':
        return render_template('register.html', datetime=datetime)  # GET 요청일 경우 register.html 렌더링


def hash_password(password):
    hash = hashlib.sha256()
    hash.update(password.encode('utf-8'))
    return hash.hexdigest()


def checkPwLen(password):
    if len(password) < 4:  # 비밀번호 길이가 4자리 미만인 경우 False 반환
        return False
    else:
        return True
    

def checkDupId(user_id):
    dup_user_id = User.query.filter_by(
        username=user_id).first()  # 중복된 username이 있는지 확인
    if dup_user_id is not None:
        return False  # 중복된 username이 있으면 False 반환
    else:
        return True


def checkEmailForm(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):  # 이메일 형식이 올바르지 않은 경우 False 반환
        return False
    else:
        return True


def checkBirthForm(birth):
    birth_regex = r'^\d{8}$'
    if not re.match(birth_regex, birth):  # 생년월일 형식이 올바르지 않은 경우 False 반환
        return False
    # 생년월일이 유효한지 검사
    try:
        year = int(birth[:4])
        month = int(birth[4:6])
        day = int(birth[6:8])
        datetime(year, month, day)
        return True
    except ValueError:
        return False
    
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']  # POST 요청으로부터 username 파라미터 추출
        password = request.form['password']  # POST 요청으로부터 password 파라미터 추출
        # username과 password가 일치하는 User 객체 추출
        user = User.query.filter_by(
            username=username, password=hash_password(password)).first()
        if user is not None:
            session['user_id'] = user.id  # 세션에 user_id 추가
            session['username'] = user.name
            return redirect(url_for('home.dashboard'))  # 대시보드 페이지로 리다이렉트
        else:
            # username 또는 password가 일치하지 않을 경우 login.html 렌더링
            return render_template('index.html', error='올바르지 않은 아이디 및 비밀번호 입니다.')
    return render_template('index.html')  # GET 요청일 경우 login.html 렌더링
