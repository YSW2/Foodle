from flask import render_template, request, redirect, url_for, session, jsonify ,abort
from fridge import fridge
from app import db
from app import app
from models import Fridge
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import openai_api.openai_api as openai_api


openai_bot = openai_api.openai_bot()


def delete_expired_foods():
    with app.app_context():
        expired_foods = Fridge.query.filter(Fridge.exp_date < datetime.today().date()).all()
        for food in expired_foods:
            db.session.delete(food)
        db.session.commit()


scheduler = BackgroundScheduler()
start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
scheduler.add_job(func=delete_expired_foods, trigger='interval', hours=24, start_date=start_time)
scheduler.start()


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
    
    # user_id에 해당하는 냉장고 음식 개수 조회
    food_count = Fridge.query.filter_by(user_id=user_id).count()

    # 냉장고 음식 개수가 30개 이상이면 오류 발생
    if food_count >= 30:
        abort(403)  # Forbidden error
    

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

@fridge.errorhandler(403)
def handle_403_error(e):
    return "30개를 초과하여 추가할 수 없습니다."


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