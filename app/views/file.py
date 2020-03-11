# -*- coding: utf-8 -*-

from typing import Optional, Any, Dict, List, Union
from uuid import uuid4
import os
from werkzeug.utils import secure_filename
from flask import request, Blueprint, current_app, send_from_directory, url_for
from flask.views import MethodView
from werkzeug.datastructures import FileStorage
from app.utils import UserError, CommonError
from app.utils import response_error, response_succ
from app.utils import get_random_num, get_unix_time_tuple, getmd5
from app.utils import session, parse_params, get_current_user
from app.utils import login_require, pages_info_requires, PageInfo, get_page_info
from app.utils import is_link, get_logger
from app.model import User, FileUserModel, FileModel

logger = get_logger(__name__)

api = Blueprint("storage", __name__)


def upload_folder():
    UPLOAD_FOLDER = current_app.config.get("UPLOAD_FOLDER")
    return UPLOAD_FOLDER


@api.route("/files/", methods=["GET"])
@login_require
@pages_info_requires
def file_list():
    """ 获得文件的列表 """
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
        .filter(FileUserModel.user_id == user.id, FileModel.file_is_delete == 0)
        .offset(pageInfo.offset)
        .limit(pageInfo.limit)
        .all()
    )
    payload: List[Dict[str, Any]] = [
        {
            "file_id": file.file_id,
            "create_time": file.file_create_time,
            "file_state": file.file_user_state,
            "file_type": file.file_type,
            "file_name": file.file_name,
            "file_url": url_for("storage.getfile", file_idf=file.file_hash),
        }
        for file in files
        if files
    ]
    return response_succ(body=payload)


@api.route("/upload/", methods=["POST"])
@login_require
def upload():
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
            target_file = ".".join([identifier, extension])
            dest: str = upload_folder()
            file.save(os.path.join(dest, target_file))
            model: FileModel = FileModel(
                filename, file_type=file.content_type, file_hash=identifier
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


@api.route("/file/<file_idf>/", methods=["GET"])
# @login_require
def getfile(file_idf: Union[int, str]):
    logger.info(file_idf)
    file: Optional[FileModel] = None
    if not file_idf:
        return CommonError.get_error(40000)
    if file_idf is int:
        # id
        file = FileModel.query.get(file_idf)
    elif isinstance(file_idf, str):
        # hash
        logger.info(file_idf)
        file = FileModel.query.filter(FileModel.file_hash == file_idf).one()
    if not file:
        return CommonError.error_toast(msg="无法找到文件")
    filehash = file.file_hash
    filename = file.file_name
    extension = filename.split(".")[-1].lower()
    targetfile = ".".join([filehash, extension])
    return send_from_directory(upload_folder(), targetfile)

