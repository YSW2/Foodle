from flask import Blueprint
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from models import Fridge
from app import db

fridge = Blueprint("fridge", __name__, template_folder="templates", static_folder="static")

'''
def delete_expired_foods():
    expired_foods = Fridge.query.filter(Fridge.expiration_date < datetime.today().date()).all()
    for food in expired_foods:
        db.session.delete(food)
    db.session.commit()

scheduler = BackgroundScheduler()
start_time = datetime.now() + timedelta(seconds=10)
scheduler.add_job(func=delete_expired_foods, trigger='interval', hours=24, start_date=start_time)
scheduler.start()'''