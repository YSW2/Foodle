from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import secrets


db = SQLAlchemy()
migate = Migrate()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = secrets.token_hex(16)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    migate.init_app(app, db)

    from auth.auth import auth as auth_blueprint
    from home.home import home as home_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(home_blueprint)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app
