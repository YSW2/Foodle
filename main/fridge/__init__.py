from flask import Blueprint

fridge = Blueprint("fridge", __name__, template_folder="templates", static_folder="static")