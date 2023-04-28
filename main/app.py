from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # 데이터베이스 설정
app.secret_key = 'secret-key'  # 세션 암호화를 위한 시크릿 키
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=True)
    birth = db.Column(db.Integer, nullable=False)


@app.route('/')
def index():
    return render_template('index.html')  # index.html 렌더링


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']  # POST 요청으로부터 username 파라미터 추출
        password = request.form['password']  # POST 요청으로부터 password 파라미터 추출
        email = request.form['email']
        birth = request.form['birth']
        
        if not checkPwLen(password):
            return render_template('register.html', error='비밀번호는 4자리 이상 설정 가능합니다.')

        if not checkDupId(username):
            return render_template('register.html', error='이미 사용중인 ID 입니다.')
        
        if not checkEmailForm(email):
            return render_template('register.html', error='이메일 형식이 올바르지 않습니다.')

        user = User(
            name=name, username=username, password=password, email=email, birth=birth
            )  # User 모델 객체 생성
        db.session.add(user)  # 데이터베이스에 추가
        db.session.commit()  # 변경사항 저장
        return redirect('/login')  # 로그인 페이지로 리다이렉트
    return render_template('register.html')  # GET 요청일 경우 register.html 렌더링

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
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']  # POST 요청으로부터 username 파라미터 추출
        password = request.form['password']  # POST 요청으로부터 password 파라미터 추출
        # username과 password가 일치하는 User 객체 추출
        user = User.query.filter_by(
            username=username, password=password).first()
        if user is not None:
            session['user_id'] = user.id  # 세션에 user_id 추가
            return redirect('/dashboard')  # 대시보드 페이지로 리다이렉트
        else:
            # username 또는 password가 일치하지 않을 경우 login.html 렌더링
            return render_template('login.html', error='올바르지 않은 아이디 및 비밀번호 입니다.')
    return render_template('login.html')  # GET 요청일 경우 login.html 렌더링


@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:  # 세션에 user_id가 있는 경우
        # user_id에 해당하는 User 객체 추출
        user = User.query.filter_by(id=session['user_id']).first()
        # dashboard.html 렌더링
        return render_template('dashboard.html', user=user)
    else:
        return redirect('/login')  # 세션에 user_id가 없는 경우 로그인 페이지로 리다이렉트


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 데이터베이스 생성
    app.run(debug=True)  # 애플리케이션 실행
