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
from app.utils import login_require, pages_info_requires, PageInfo, get_page_info
from app.utils import is_link, get_logger
from app.model import User, FileUserModel, FileModel
import app

logger = get_logger(__name__)

api = Blueprint("storage", __name__)
app.fetch_route(api, "/storage")


@api.route("/files", methods=["GET"])
@login_require
@pages_info_requires
def file_list():
    user: User = get_current_user()
    pageInfo: PageInfo = get_page_info()
    files = (
        session.query(
            FileModel.file_id,
            FileModel.file_hash,
            FileModel.file_name,
            FileModel.file_create_time,
            FileModel.file_type,
            FileUserModel.file_user_state,
            FileUserModel.add_time,
        )
        .join(FileUserModel, FileUserModel.file_id == FileModel.file_id)
        .filter(FileUserModel.file_user_id == user.id, FileModel.file_is_delete == 0)
        .offset(pageInfo.offset)
        .limit(pageInfo.limit)
        .all()
    )
    logger.info(files)
    payload: List[Dict[str, Any]] = [
        {
            "file_id": file.file_id,
            "create_time": file.file_create_time,
            "file_state": file.file_user_state,
            "file_type": file.file_type,
            "file_url": fileStorage.url(file.file_hash),
            "file_name": file.file_name,
        }
        for file in files
        if files
    ]
    return response_succ(body=payload)


class FileStoreView(MethodView):
    decorators = [login_require]

    def get(self, file_idf: Optional[Union[int, str]]):
        if not file_idf:
            return CommonError.get_error(40000)
        if file_idf is int:
            # id
            pass
        else:
            # hash
            pass
        return response_succ()

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
                    filename, file_type=file.content_type, file_hash=identifier
                )
                name: str = fileStorage.save(
                    file,
                    name="{identifier}".format(
                        identifier=identifier
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
        user: User = get_current_user()
        relationship = FileUserModel.query.filter(
            FileUserModel.user_id == user.id, FileUserModel.file_id == file_id
        ).one()
        relationship.file_user_state = 4
        relationship.save(commit=True)
        return response_succ(toast="删除成功")

    def put(self, file_id: Optional[Union[int, str]]):
        pass


file_view = FileStoreView.as_view("file_api")
api.add_url_rule("/file/<file_idf>", view_func=file_view, methods=["GET", "DELETE"])
api.add_url_rule("/upload", view_func=file_view, methods=["POST"])
