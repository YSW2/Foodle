from flask import render_template, redirect, session
from auth.models import User
from home import home


@home.route('/dashboard')
def dashboard():
    if 'user_id' in session:  # 세션에 user_id가 있는 경우
        # user_id에 해당하는 User 객체 추출
        user = User.query.filter_by(id=session['user_id']).first()
        # dashboard.html 렌더링
        return render_template('dashboard.html', user=user)
    else:
        return redirect('/')  # 세션에 user_id가 없는 경우 로그인 페이지로 리다이렉트
