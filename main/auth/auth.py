from flask import render_template, redirect, request, session
from auth.models import User
from datetime import datetime
from app import db
from auth import auth
import hashlib
import re


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']  # POST 요청으로부터 username 파라미터 추출
        password = request.form['password']  # POST 요청으로부터 password 파라미터 추출
        email = request.form['email']
        birth = str(request.form['birth'])
        
        if not checkPwLen(password):
            return render_template('register.html', error='비밀번호는 4자리 이상 설정 가능합니다.')

        if not checkDupId(username):
            return render_template('register.html', error='이미 사용중인 ID 입니다.')
        
        if not checkEmailForm(email):
            return render_template('register.html', error='이메일 형식이 올바르지 않습니다.')
        
        if not checkBirthForm(birth):
            return render_template('register.html', error='생년월일을 올바르게 입력해주세요.')

        user = User(
            name=name, username=username, password=hash_password(password), email=email, birth=datetime(int(birth[:4]), int(birth[4:6]), int(birth[6:8]))
            )  # User 모델 객체 생성    
        db.session.add(user)  # 데이터베이스에 추가
        db.session.commit()  # 변경사항 저장
        return redirect('/login')  # 로그인 페이지로 리다이렉트
    return render_template('register.html')  # GET 요청일 경우 register.html 렌더링

def hash_password(password):
    hash = hashlib.sha256()
    hash.update(password.encode('utf-8'))
    return hash.hexdigest()

def checkPwLen(password):
    if len(password) < 4:
        return False
    else: 
        return True
    
def checkDupId(user_id):
    dup_user_id = User.query.filter_by(username=user_id).first()
    if dup_user_id is not None:
        return False
    else:
        return True
    
def checkEmailForm(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return False
    else:
        return True

def checkBirthForm(birth):
    birth_regex = r'^\d{8}$'
    if not re.match(birth_regex, birth):
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
            return redirect('/dashboard')  # 대시보드 페이지로 리다이렉트
        else:
            # username 또는 password가 일치하지 않을 경우 login.html 렌더링
            return render_template('login.html', error='올바르지 않은 아이디 및 비밀번호 입니다.')
    return render_template('login.html')  # GET 요청일 경우 login.html 렌더링
