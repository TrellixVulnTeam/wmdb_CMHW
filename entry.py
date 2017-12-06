from flask import Blueprint

entry_api = Blueprint('entry_api', __name__)


@entry_api.route("/entry")
def entry_index():
    return "entry index"
