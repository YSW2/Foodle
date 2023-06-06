from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(50), nullable=True)
    birth = db.Column(db.Date, nullable=False)
    posts = db.relationship('Post')


class Post(db.Model):
    __tablename__ = 'post'
        
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    like = db.Column(db.Integer, default=0)
    view = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Fridge(db.Model):
    __tablename__ = 'fridge'

    id = db.Column(db.Integer, primary_key=True)
    food = db.Column(db.Text, nullable=False)
    exp_date = db.Column(db.Date, nullable=True)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
    
    
class Like(db.Model):
    __tablename__ = 'like'
    
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)