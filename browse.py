from flask import Blueprint

browse_api = Blueprint('browse_api', __name__)


@browse_api.route("/browse")
def browse_index():
    return "browse index"
