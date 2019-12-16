from typing import Optional, AnyStr, Dict
from flask import request, Blueprint
from app.utils import UserError, CommonError
from app.utils import response_error, response_succ
from app.utils import get_random_num, get_unix_time_tuple, getmd5
from app.utils import session, parse_params, get_current_user
from app.utils import login_require
from app.model import User, TodoModel
import app

api = Blueprint("todo", __name__)
app.fetch_route(api, "/todo")


@api.route("/add", methods=["POST"])
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


def set_todo_state(todo_id: int, state: int) -> Optional[Dict[AnyStr, any]]:
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


@api.route("/finish", methods=["POST"])
@login_require
def finish_todo():
    params = parse_params(request)
    todo_id = params.get("todo_id")
    result = set_todo_state(todo_id, 2)
    if not result:
        return CommonError.get_error(40000)
    return response_succ(body=result)


@api.route("/remove", methods=["POST"])
@login_require
def remove_todo():
    params = parse_params(request)
    todo_id = params.get("todo_id")
    result = set_todo_state(todo_id, 3)
    if not result:
        return CommonError.get_error(40000)
    return response_succ(body=result)


@api.route("/filter/<string:filter>", methods=["POST"])
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
    result = list()
    if not todos or len(todos) == 0:
        response_succ(body=())
    for todo in todos:
        result.append(
            {
                "todo_id": todo.todo_id,
                "todo_title": todo.todo_title,
                "todo_state": todo.todo_state,
            }
        )
    return response_succ(body=result)


@api.route("/undo", methods=["POST"])
@login_require
def undo_todo():
    params = parse_params(request)
    todo_id = params.get("todo_id")
    result = set_todo_state(todo_id, 1)
    if not result:
        return CommonError.get_error(40000)
    return response_succ(body=result)