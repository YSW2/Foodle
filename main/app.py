from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import secrets

# SQLAlchemy와 Migrate 객체 생성
db = SQLAlchemy()
migate = Migrate()

# Flask 애플리케이션 생성


def create_app():
    app = Flask(__name__)

    # 애플리케이션 설정
    app.config['SECRET_KEY'] = secrets.token_hex(16)  # 시크릿 키 생성
    # 데이터베이스 경로 설정
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 데이터베이스 변경사항 추적 비활성화

    # SQLAlchemy와 Migrate 객체 초기화
    db.init_app(app)
    migate.init_app(app, db)

    # 블루프린트 등록
    from auth.auth import auth as auth_blueprint
    from home.home import home as home_blueprint

    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    app.register_blueprint(home_blueprint)

    # '/' 경로로 접속 시 auth 블루프린트의 login 함수로 리다이렉트
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app
