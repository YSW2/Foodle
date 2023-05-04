from flask import Blueprint

board = Blueprint("board", __name__, template_folder="templates", static_folder="static")