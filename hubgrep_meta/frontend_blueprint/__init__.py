from flask import Blueprint, render_template
from flask import current_app as app

frontend = Blueprint("frontend", __name__)

@frontend.route("/")
def index():
    return "Hello world!"

