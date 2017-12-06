from flask import Blueprint

search_api = Blueprint('search_api', __name__)


@search_api.route("/search")
def search_index():
    return "search index"
