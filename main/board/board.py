from flask import render_template, redirect, session, url_for, request, jsonify, abort
from models import Post
from app import db
from board import board
from datetime import datetime
from flask_paginate import Pagination,  get_page_args
from sqlalchemy import or_
import random


@board.route('/', methods=['GET', 'POST'])
def list_post():
    page = request.args.get('page',type=int,default=1)
    per_page = request.args.get('per_page',type=int,default=10)
    option = request.args.get('option',type=str,default='T')
    keyword = request.args.get('keyword',type=str,default='')
    posts = Post.query.order_by(Post.created_at.desc())  # 최신순으로 게시글 정렬
    
        # 제목으로 검색
    if option == 'T' and keyword != '':
        posts = posts.filter(Post.title.ilike(f"%{keyword}%"))

        # 내용으로 검색
    elif option == 'C' and keyword != '':
        posts = posts.filter(Post.content.ilike(f"%{keyword}%"))

        # 제목 또는 내용으로 검색
    elif option == 'TC' and keyword != '':
        posts = posts.filter(or_(Post.title.ilike(f"%{keyword}%"), Post.content.ilike(f"%{keyword}%")))
        
    posts = posts.paginate(page=page,per_page=per_page)
    return render_template('list_post.html', posts=posts,option=option,keyword=keyword)



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
                        created_at=now, view=0, like=0,user_id=session['user_id'])  # 새로운 게시물 생성
        post_db_session = db.session(bind='post')  # 게시물 DB 세션 생성
        post_db_session.add(new_post)  # 새로운 게시물 추가
        post_db_session.commit()  # DB에 반영
        return redirect(url_for('board.list_post'))  # 게시물 목록 페이지로 이동
    return render_template('write.html')  # GET 요청일 경우 게시물 작성 페이지 렌더링


@board.route('/<int:post_id>', methods=['GET'])
def show_post(post_id):
    page = request.args.get('page',type=int,default=1)
    per_page = request.args.get('per_page',type=int,default=10)
    option = request.args.get('option',type=str,default='T')
    keyword = request.args.get('keyword',type=str,default='')
    
    post = Post.query.get_or_404(post_id)
    post.view += 1
    db.session.commit()
    return render_template('post.html', post=post,page=page,per_page=per_page,option=option,keyword=keyword)



@board.route('/<int:post_id>', methods=['POST'])
def Like_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.like += 1
    db.session.commit()
    response = {'like': post.like}
    return jsonify(response)


@board.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page',type=int,default=1)
    per_page = request.args.get('per_page',type=int,default=10)
    option = request.args.get('option',type=str,default='T')
    keyword = request.args.get('keyword',type=str,default='')

    
    # 게시물 작성자와 로그인한 사람이 동일하지 체크
    if('user_id' not in session or post.user_id != session['user_id']):
        abort(403)  # Forbidden error

    db.session.delete(post)
    db.session.commit()

    return redirect(url_for('board.list_post',page=page,per_page=per_page,option=option,keyword=keyword))


@board.route('/modify/<int:post_id>', methods=['POST'])
def modify_post(post_id):
    post = Post.query.get_or_404(post_id)
    if('user_id' not in session or post.user_id != session['user_id']):
        abort(403)  # Forbidden error
    title = request.form.get('title')
    content = request.form.get('content')

    post.title = title
    post.content = content
    post.created_at = datetime.now()
    db.session.commit()
    
    response = {'title': post.title,'content':content}
    return jsonify(response)


# paging 테스트를 위해 , 게시물 100개 작성
@board.route('/hiddencreate')
def create_posts():
    for i in range(1, 101):
        title = f"게시물 제목 {i}"
        content = f"게시물 내용 {random.randint(1, 100)}"
        author = session['username']
        new_post = Post(title=title, content=content, author=author,
                        created_at=datetime.now(), view=0, like=0,user_id=session['user_id'])  # 새로운 게시물 생성

        db.session.add(new_post)  # 새로운 게시물 추가
    db.session.commit()
    print("게시물 생성이 완료되었습니다.")
    return redirect(url_for('board.list_post'))


# 게시물 모두 삭제
@board.route('/hiddendelete')
def delete_all_posts():
    db.session.query(Post).delete()
    db.session.commit()
    return redirect(url_for('board.list_post'))