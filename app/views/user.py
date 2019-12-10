from flask import request, current_app, g
from ..views import api
from app.utils.errors import UserError
from app.utils import get_random_num, get_unix_time_tuple, getmd5
from app.models import User, db

@api.route('/user/register', methods=['POST'])
def register():
    params = request.values or request.get_json() or {}
    email = params.get("email")
    password = params.get("password")
    if len(password) != 32:
        return UserError.get_error(40000)
    exsist_user = db.session.query(User).filter_by(email=email).first()
    if exsist_user:
        return UserError.get_error(40200)
    salt = current_app.config['SECURITY_PASSWORD_SALT'] or 'token'
    token = getmd5("{}{}{}".format(salt, email, get_random_num(5)))
    user = User(email=email, password=password, status=1)
    user.token = token
    db.session.add(user)
    db.session.commit()
    payload = {}
    payload['user_id'] = user.id
    return response_succ(body=payload)