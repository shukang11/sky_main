from flask import Blueprint
import app

api: Blueprint = Blueprint('api', __name__)
root: Blueprint = Blueprint('root', __name__)

from app.views import uploads

app.fetch_route(api, '/api')
app.fetch_route(root, '/')
