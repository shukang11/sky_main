from typing import Optional, Dict
from flask import request, current_app, g, Blueprint
from app.utils import UserError, CommonError, NoResultFound, MultipleResultsFound
from app.utils import response_error, response_succ
from app.utils import get_random_num, get_unix_time_tuple, getmd5
from app.utils import session, parse_params, get_current_user, get_logger, redis_client
from app.utils import login_require, get_token_from_request, is_phone, is_email
from app.model import User, LoginRecordModel

api = Blueprint("user", __name__)

logger = get_logger(__name__)

def register():
    params = parse_params(request)
    email: str = params.get("email")
    password: str = params.get("password")
    q = session.query(User).filter(User.email == email, User.password == password)
    exsist_user = session.query(q.exists()).scalar()
    if exsist_user:
        return UserError.get_error(error_code=40200)
    user = User(email, password=password)
    try:
        session.add(user)
        session.commit()
        payload: Dict[str, int] = {"user_id": user.id}
        return response_succ(body=payload)
    except Exception as e:
        return CommonError.get_error(error_code=9999)


def login():
    params = parse_params(request)
    email: Optional[str] = params.get("email")
    password: Optional[str] = params.get("password")
    if not email or not password:
        return CommonError.get_error(error_code=40000)
    try:
        exsist_user: User = session.query(User).filter_by(
            email=email, password=password
        ).one()
        login_time: str = get_unix_time_tuple()
        log_ip: str = request.args.get("user_ip") or request.remote_addr
        record: LoginRecordModel = LoginRecordModel(exsist_user.id, log_ip)
        record.save()
        # update token
        token: str = getmd5("-".join([email, password, get_random_num(2)]))
        # 保存到redis中, 设置有效时间为7天
        cache_key: str = exsist_user.get_cache_key
        time: int = 60 * 60 * 24 * 7
        redis_client.client.set(cache_key, token, time)
        redis_client.client.set(token, cache_key, time)
        payload: Dict[str, any] = {"token": token, "user_id": exsist_user.id}
        return response_succ(body=payload)
    except NoResultFound:
        return UserError.get_error(40203)
    except Exception as e:
        logger.error(e)
        return CommonError.get_error(9999)
    

@login_require
def logout():
    """  登出
    设置redis时间为过期
    """
    params = parse_params(request)
    token = get_token_from_request(request)
    user: User = get_current_user()
    cache_key: str = user.get_cache_key
    redis_client.client.delete(cache_key, token)
    return response_succ(body={})


@login_require
def user_info():
    """  获得用户基本信息 
    需要登录权限
    """
    params = parse_params(request)
    user: User = get_current_user()
    payload: Dict[str, Any] = user.info_dict
    return response_succ(body=payload)


@login_require
def modify_user_info():
    params = parse_params(request)
    user: User = get_current_user()
    # 用户昵称
    nickname =params.get("nickname")
    phone = params.get("phone")
    sex = int(params.get("sex"))
    email = params.get("email")
    if nickname:
        user.nickname = nickname
    if phone:
        if is_phone(str(phone)) and len(phone) == 11:
            user.mobilephone = phone
        else: return CommonError.error_toast(msg="手机号码格式错误")
    if sex:
        if sex in (1, 0):
            user.sex = sex
        else: return CommonError.error_toast(msg="性别设置错误")
    if email:
        if is_email(email):
            user.email = email
        else: return CommonError.error_toast(msg="邮箱格式错误")
    user.save(commit=True)
    payload: Dict[str, Any] = user.info_dict
    return response_succ(body=payload)

def mail_one_time_code(f: str):
    pass


def setup_url_rule(api: Blueprint):
    # 注册
    api.add_url_rule("/register", view_func=register, methods=["POST"])
    # 登录
    api.add_url_rule("/login", view_func=login, methods=["POST"])
    # 修改信息
    api.add_url_rule("/modify_info", view_func=modify_user_info, methods=["POST"])
    # 获得用户信息
    api.add_url_rule("/info", view_func=user_info, methods=["GET"])
    # 登出
    api.add_url_rule("/logout", view_func=logout, methods=["POST"])


setup_url_rule(api)
