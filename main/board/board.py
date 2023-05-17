from flask import render_template, redirect, session, url_for, request, jsonify
from board.post_models import Post
from app import db
from board import board
from datetime import datetime


@board.route('/', methods=['GET', 'POST'])
def list_post():
    posts = Post.query.order_by(Post.created_at.asc()).all() # 최신순으로 게시글 정렬
    return render_template('list_post.html', posts=posts)


@board.route('/upload', methods=['GET', 'POST'])
def write_post():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':  # POST 요청일 경우
        title = request.form['title']  # 제목 가져오기
        content = request.form['content']  # 내용 가져오기
        author = session['username']  # 작성자 정보 가져오기
        now = datetime.now()  # 현재 시간 가져오기
        new_post = Post(title=title, content=content, author=author,
                        created_at=now, view=0, like=0)  # 새로운 게시물 생성
        post_db_session = db.session(bind='post')  # 게시물 DB 세션 생성
        post_db_session.add(new_post)  # 새로운 게시물 추가
        post_db_session.commit()  # DB에 반영
        return redirect(url_for('board.list_post'))  # 게시물 목록 페이지로 이동
    return render_template('write.html')  # GET 요청일 경우 게시물 작성 페이지 렌더링


@board.route('/<int:post_id>', methods=['GET'])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.view += 1
    db.session.commit()
    return render_template('post.html', post=post)


@board.route('/<int:post_id>', methods=['POST'])
def Like_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.like += 1
    db.session.commit()
    response = {'like': post.like}
    return jsonify(response)