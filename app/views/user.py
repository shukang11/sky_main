from typing import Optional, AnyStr, Dict
from flask import request, current_app, g
from ..views import api
from app.utils.errors import UserError
from app.utils.response import response_error, response_succ
from app.utils import get_random_num, get_unix_time_tuple, getmd5
from app.utils import redisClient
from app.models import db, User, LoginRecord, User

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
    
    user = User(email, password, 1)
    user.save()
    payload = {}
    payload['user_id'] = user.id
    return response_succ(body=payload)


@api.route('/user/login', methods=['POST'])
def login():
    params = request.values or request.get_json() or {}
    email: str = params.get("email")
    password: str = params.get("password")
    exsist_user: User = db.session.query(User).filter_by(email=email, password=password).first()
    if exsist_user:
        # update log time
        login_time: str = get_unix_time_tuple()
        log_ip: str = request.args.get("user_ip") or request.remote_addr
        record: LoginRecord = LoginRecord(exsist_user.user_id, login_time=login_time, ip=log_ip)
        record.save()
        # update token
        token: AnyStr = getmd5("-".join([email, password, login_time]))
        # 保存到redis中, 设置有效时间为7天
        redisClient.set(str(exsist_user.id), token, 60*60*24*7)
        return response_succ(body={'token': token})
    else:
        return UserError.get_error(40203)


@api.route('/user/logout', methods=['POST'])
def logout():
    """  登出
    设置redis时间为过期
    """
    pass

@api.route('/test', methods=['GET', 'POST'])
def hello():
    params: Dict[AnyStr, any] = dict(request.values or request.get_json() or {})
    redisClient.incr('/test')
    params['hits'] = int(redisClient.get('/test'))
    return response_succ(body=params)