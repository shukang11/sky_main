# -*- coding: utf-8 -*-


from app.utils.response import response_error


class ApiError:
    @classmethod
    def get_error(cls, error_code):
        raise NotImplementedError


class CommonError(ApiError):
    @classmethod
    def get_error(cls, error_code: int=9999):
        switcher = {
            # 未知错误
            9999: response_error(error_code=9999, msg="unknown_error", http_code=400),
            # 参数不全或错误
            40000: response_error(
                error_code=40000, msg="args_missing_or_wrong", http_code=400
            ),
            # token 过期
            40204: response_error(error_code=40204, msg="token expired", http_code=400),
            # 需要权限
            43000: response_error(
                error_code=43000, msg="need_permission", http_code=401
            ),
            # 资源不存在
            44000: response_error(error_code=44000, msg="url_not_found", http_code=404),
        }
        resp = switcher.get(error_code or 9999)
        assert resp != None
        return resp

    @classmethod
    def error_toast(cls, msg="error_message"):
        return response_error(error_code=40001, msg=msg, http_code=400)


class UserError(CommonError):
    """ 用户模块下的错误类型包装 """

    @classmethod
    def get_error(cls, error_code):
        switcher = {
            # 账号已存在
            40200: response_error(
                error_code=40200, msg="account_exsist", http_code=400
            ),
            # 无此账号，无法找出用户
            40203: response_error(error_code=40203, msg="no_account", http_code=400),
        }
        return switcher.get(error_code) or super(UserError, cls).get_error(error_code)
