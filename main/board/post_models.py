from app import db
from datetime import datetime

class Post(db.Model):
    __bind_key__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    like = db.Column(db.Integer, default=0)
    view = db.Column(db.Integer, default=0)