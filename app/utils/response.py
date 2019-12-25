from typing import Dict, Tuple, Optional, Union, List, Any
from flask import jsonify, Response


def __check_request(method: str = "") -> str:
    """
    检查返回的错误信息是否合规则
    :param request: 返回的请求地址
    :return: 如果请求的地址为空，则返回空字符串
    """
    methods: List[str] = ['get', 'post', 'put', 'patch', 'delete', '*']
    request: str = method.lower()
    request = request.strip()
    if len(request) == 0:
        return ""

    for method in methods:
        if request.startswith(method):
            request = request.replace(method, method.upper())
            break
    else:
        request = "GET {}".format(request)
    return request


def __error_handler(
    msg: Optional[str] = None,
    code: int = 404,
    request: Optional[str] = None,
    data: Any = None
) -> Dict[str, Any]:
    """
    将不正确的参数格式化返回
    :param msg: 错误信息
    :param code: 错误码
    :param request: 下一步的链接(可选)
    :return: 组装的字典对象
    """
    result: Dict[str, Any] = {}
    request = __check_request(request or "")
    result["code"] = code
    result["msg"] = msg or ""
    if len(request) > 0:
        result["request"] = request or ""
    result['data'] = data
    return result


def response_succ(
    body: Union[Dict[str, Any], List[Any]] = {},
    status_code: int = 200,
    header: Optional[Dict] = None,
    toast: Optional[str] = None
) -> Tuple[Dict[str, Any], int, Dict[str, str]]:
    """返回一个成功的报文
    对返回值进行统一的包装，避免有多种返回值格式

    Args:
        status_code: 状态值，成功的可选值应该是[200, 201, 202, 204]中的一个
        body: 返回的报文内容
        header: 返回头的内容

    200 OK - [GET]：服务器成功返回用户请求的数据，该操作是幂等的（Idempotent）。
    201 CREATED - [POST/PUT/PATCH]：用户新建或修改数据成功。
    202 Accepted - [*]：表示一个请求已经进入后台排队（异步任务）
    204 NO CONTENT - [DELETE]：用户删除数据成功。

    Returns:
        返回一个元祖，包含了[返回值，状态码，返回头]

    Raises:
        ValueError: 如果状态码不在200段，则抛出异常; 如果无法将返回值解析为json，则抛出异常
    """
    success_codes = [200, 201, 202, 204]
    if status_code not in success_codes:
        raise ValueError("statusCode is not in successCodes")
    try:
        result: Dict[str, Any] = {
            "data": body,
            "msg": toast or "",
            "code": status_code
        }
        if result:
            result = jsonify(result)
    except Exception as _:
        raise ValueError("Unknown body")
    if header is None:
        header = {
            # 'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*'
        }
    return result, status_code, header


def response_error(
    error_code: int = 0,
    msg: str = None,
    http_code: int = 0,
    header: Optional[Dict] = None
) -> Tuple[str, int, Dict[str, str]]:
    """  对一个返回错误包装
    包装格式，保持统一
    Args:
        error_code: 状态值，错误的可选值应该是根据具体的模块中定义的
        msg: 返回的错误内容
        http_code: 状态值，错误的可选值应该是下文`error_codes`中的一个
        header: 返回头的内容

    400 INVALID REQUEST - [POST/PUT/PATCH]：用户发出的请求有错误，服务器没有进行新建或修改数据的操作，该操作是幂等的。
    401 Unauthorized - [*]：表示用户没有权限（令牌、用户名、密码错误）。
    403 Forbidden - [*] 表示用户得到授权（与401错误相对），但是访问是被禁止的。
    404 NOT FOUND - [*]：用户发出的请求针对的是不存在的记录，服务器没有进行操作，该操作是幂等的。
    406 Not Acceptable - [GET]：用户请求的格式不可得（比如用户请求JSON格式，但是只有XML格式）。
    410 Gone -[GET]：用户请求的资源被永久删除，且不会再得到的。
    422 Unprocesable entity - [POST/PUT/PATCH] 当创建一个对象时，发生一个验证错误。
    500 INTERNAL SERVER ERROR - [*]：服务器发生错误，用户将无法判断发出的请求是否成功。

    :return: 返回一个响应
    """
    from flask import request as r
    error_codes = [400, 401, 402, 403, 404, 406, 410, 500]
    if msg is None:
        raise ValueError("error Msg can't be None")
    if msg and http_code not in error_codes:
        raise ValueError("error and successCode can't both exists")
    if header is None:
        header = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Method': '*'
        }
    data = __error_handler(msg=msg,
                           code=error_code,
                           request="{0} {1}".format(r.method, r.path))

    return jsonify(data) or jsonify({"error": "cant jsonify"}), http_code, header
