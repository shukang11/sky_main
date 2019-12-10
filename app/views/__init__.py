from flask import Blueprint
import app

api: Blueprint = Blueprint('api', __name__)

from app.views import uploads

app.route_list(api, '/api')