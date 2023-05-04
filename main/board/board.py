from flask import render_template, redirect, session, url_for, request
from board.post_models import Post
from app import db
from board import board
from datetime import datetime


@board.route('/', methods=['GET', 'POST'])
def list_post():
    posts = Post.query.order_by(Post.created_at.desc()).all() # 최신순으로 게시글 정렬
    return render_template('list_post.html', posts=posts)


@board.route('/upload', methods=['GET', 'POST'])
def write_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author = request.form['author']
        now = datetime.now()
        new_post = Post(title=title, content=content, author=author, created_at=now, like=0, view=0)
        post_db_session = db.session(bind='post')
        post_db_session.add(new_post)
        post_db_session.commit()
        return redirect(url_for('board.list_post'))
    return render_template('write.html')


@board.route('/<int:post_id>')
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)