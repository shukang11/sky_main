from typing import Optional, Dict, Any, List
from flask import request, Blueprint
from app.utils import UserError, CommonError, NoResultFound
from app.utils import response_error, response_succ
from app.utils import get_random_num, get_unix_time_tuple, getmd5
from app.utils import session, parse_params, get_current_user
from app.utils import login_require
from app.model import User, TodoModel

api = Blueprint("todo", __name__)


@login_require
def add_todo():
    """ add todo by parameters

    try to add a todo to todolist,you can just set the todo title.

    Args:
        title: title of the todo item

    Returns:
        a dict mapping keys to the index of the todo item just added.
        example:
        {"todo_id": 6}

    """

    params = parse_params(request)
    user: User = get_current_user()
    title = params.get("title")
    try:
        todo = TodoModel()
        todo.todo_title = title
        todo.add_time = get_unix_time_tuple()
        todo.todo_state = 1
        todo.bind_user_id = user.id
        todo.save(True)
        result = {"todo_id": todo.todo_id}
        return response_succ(body=result)
    except Exception as e:
        return CommonError.get_error(error_code=9999)


def set_todo_state(todo_id: int, state: int) -> Optional[Dict[str, Any]]:
    """ change a todo item state

    try to modify a todo_state, option (1, 2, 3)

    Args:
        todo_id: the id of the todo item you wanna change.
        state: state value, 1: undo, 2: done, 3: removed

    Returns:
        a dict mapping keys to the structure of the todo item just changed, if change failed, return None.
        example:
        {
            "todo_id": 4,
            "todo_title": "test todo",
            "todo_state": 2
        }

    Raises:
        NoResultFound: An error occurred when A database result was required but none was found.

    """

    result = None
    try:
        todo: Optional[TodoModel] = session.query(TodoModel).filter_by(
            todo_id=todo_id
        ).one()
        if not todo:
            return result
        todo.todo_state = state
        todo.save(True)
        result = {
            "todo_id": todo.todo_id,
            "todo_title": todo.todo_title,
            "todo_state": todo.todo_state,
        }
    except NoResultFound as e:
        result = None
    return result


@login_require
def finish_todo():
    params = parse_params(request)
    todo_id = params.get("todo_id")
    result = set_todo_state(todo_id, 2)
    if not result:
        return CommonError.get_error(40000)
    return response_succ(body=result)


@login_require
def remove_todo():
    params = parse_params(request)
    todo_id = params.get("todo_id")
    result = set_todo_state(todo_id, 3)
    if not result:
        return CommonError.get_error(40000)
    return response_succ(body=result)


@login_require
def filter_todo(filter: str = None):
    params = parse_params(request)
    user: User = get_current_user()
    option_filter = filter or "all"
    todos = session.query(TodoModel).filter(TodoModel.bind_user_id == user.id)

    if option_filter == "undo":
        todos = todos.filter(TodoModel.todo_state == 1).all()
    if option_filter == "done":
        todos = todos.filter(TodoModel.todo_state == 2).all()
    if option_filter == "all":
        todos = todos.filter(TodoModel.todo_state != 3).all()
    result: List[Dict[str, Any]] = [
        {
            "todo_id": todo.todo_id,
            "todo_title": todo.todo_title,
            "todo_state": todo.todo_state,
        }
        for todo in todos
        if todos
    ]
    return response_succ(body=result)


@login_require
def undo_todo():
    params = parse_params(request)
    todo_id = params.get("todo_id")
    result = set_todo_state(todo_id, 1)
    if not result:
        return CommonError.get_error(40000)
    return response_succ(body=result)


def setup_url_rule(api: Blueprint):
    # 添加待办事项
    api.add_url_rule("/add", view_func=add_todo, methods=["POST"])
    # 结束待办
    api.add_url_rule("/finish", view_func=finish_todo, methods=["POST"])
    # 移除待办
    api.add_url_rule("/remove", view_func=remove_todo, methods=["POST"])
    # 筛选待办列表
    api.add_url_rule("/filter/<string:filter>", view_func=filter_todo, methods=["POST"])
    # 撤销结束
    api.add_url_rule("/undo", methods=["POST"])


setup_url_rule(api)
