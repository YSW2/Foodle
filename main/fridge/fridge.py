from flask import render_template, request, redirect, url_for, session
from fridge import fridge
from app import db
from models import Fridge, User
from datetime import datetime



@fridge.route('/', methods=['GET'])
def myfridge():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    if user:
        foods = Fridge.query.filter_by(user_id=user.id).all()
    else:
        foods = []
    
    return render_template('fridge.html', user_name=session['username'], foods=foods)


@fridge.route('/update', methods=['POST'])
def updatefridge():
    food = request.form['food']
    exp_date_str = request.form['exp_date']
    user_id = session['user_id']
    
    # 유통기한이 비어있으면 None으로 설정
    if not exp_date_str:
        exp_date = None
    
    else:
        exp_date = datetime.strptime(exp_date_str, '%Y%m%d').date()

    # 냉장고 음식 생성
    fridge_food = Fridge(user_id=user_id, food=food, exp_date=exp_date)
    db.session.add(fridge_food)
    db.session.commit()

    return redirect(url_for('fridge.myfridge'))


@fridge.route('/delete/<int:food_id>', methods=['POST'])
def deletefood(food_id):
    fridge_food = Fridge.query.get(food_id)
    if fridge_food:
        db.session.delete(fridge_food)
        db.session.commit()
        
    return redirect(url_for('fridge.myfridge'))