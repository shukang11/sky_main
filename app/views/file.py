# -*- coding: utf-8 -*-

from typing import Optional, Any, Dict, List, Union
from uuid import uuid4
from flask import request, Blueprint
from flask.views import MethodView
from werkzeug.datastructures import FileStorage
from app.utils import fileStorage
from app.utils import UserError, CommonError
from app.utils import response_error, response_succ
from app.utils import get_random_num, get_unix_time_tuple, getmd5
from app.utils import session, parse_params, get_current_user
from app.utils import login_require
from app.utils import is_link, get_logger
from app.model import User, FileUserModel, FileModel
import app

logger = get_logger(__name__)

api = Blueprint("storage", __name__)
app.fetch_route(api, "/storage")


class FileStoreView(MethodView):
    decorators = [login_require]

    def get(self, file_id: Optional[Union[int, str]]):
        pass

    def post(self):
        params = parse_params(request)
        user: User = get_current_user()
        files: Optional[List[FileStorage]] = request.files.getlist("files")
        if len(files) == 0:
            return CommonError.get_error(40000)
        payload: List[FileModel] = []
        file_user: List[FileUserModel] = []
        try:
            for file in files:
                filename: str = file.filename
                # 拓展名
                extension = filename.split(".")[-1].lower()
                # uuid
                identifier = str(uuid4()).replace("-", "")
                model: FileModel = FileModel(
                    filename, file_type=extension, file_hash=identifier
                )
                name: str = fileStorage.save(
                    file,
                    name="{identifier}.{extension}".format(
                        identifier=identifier, extension=extension
                    ),
                )
                payload.append(model)
                session.add(model)
                session.flush()
                # relation ship
                relationship: FileUserModel = FileUserModel(
                    user_id=user.id, file_id=model.file_id
                )
                file_user.append(relationship)
                session.add(relationship)
                session.flush()
            session.commit()
            result: List[Dict[str, Any]] = [
                {"file_id": f.file_id, "file_hash": f.file_hash} for f in payload
            ]
            return response_succ(body=result)
        except Exception as e:
            logger.error(e)
            return CommonError.get_error(9999)

    def delete(self, file_id: Optional[Union[int, str]]):
        pass

    def put(self, file_id: Optional[Union[int, str]]):
        pass


file_view = FileStoreView.as_view("file_api")
api.add_url_rule("/file/<file_id>", view_func=file_view, methods=["GET", "DELETE"])
api.add_url_rule("/upload", view_func=file_view, methods=["POST"])
