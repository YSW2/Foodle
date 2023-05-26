from flask import render_template, request, redirect, url_for, session, jsonify
from fridge import fridge
from app import db
from models import Fridge
from datetime import datetime
import openai_api.openai_api as openai_api


openai_bot = openai_api.openai_bot()


@fridge.route('/', methods=['GET'])
def myfridge():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    openai_bot.messages_clear()
    foods = Fridge.query.filter_by(user_id=session['user_id']).all()
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


@fridge.route('/recommend_recipe', methods=['POST'])
async def recommend_recipe():
    data = request.data.decode("utf-8")
    if data == 'recommendation':
        foods = Fridge.query.filter_by(user_id=session['user_id']).all()
        if len(foods) >= 3:
            food_list = ''
            for food in foods:
                food_list += f'{food.food} '
            question = '다음과 같은 재료가 있습니다: ' + food_list + '이 재료들로 요리 레시피를 한 개 알려주세요.'
            response = await openai_bot.usegpt(question)
        else:
            response = '최소 세 가지 이상의 재료가 있어야 합니다.'
    elif data == 'retry':
        question = '다른 레시피를 한 개 더 알려주세요.'
        response = await openai_bot.usegpt(question)

    result = {'recipe' : response}
    return jsonify(result)