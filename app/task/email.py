from typing import List, Union
import os
from flask import render_template
from app.utils import get_logger
from app.utils import celery_app
from app.config import configInfo
from app.extension import Mail, Message

logger = get_logger(__name__)


@celery_app.task(name="web_task.send_email")
def send_email(
    subject: str,
    recipients: List[str],
    sender: Union[str] = None,
    html: Union[None, str] = None,
    body: Union[None, str] = None,
):
    env: str = os.getenv("FLASK_ENV") or "develop"
    config = configInfo[env]
    if not config:
        return
    server: str = getattr(config, "MAIL_SERVER")
    port: int = getattr(config, "MAIL_PORT")
    use_ssl: bool = getattr(config, "MAIL_USE_SSL")
    use_tls: bool = getattr(config, "MAIL_USE_TLS")
    username: str = getattr(config, "MAIL_USERNAME")
    password: str = getattr(config, "MAIL_PASSWORD")
    sender = sender or getattr(config, "MAIL_DEFAULT_SENDER")

    mail_client = Mail(
        server, username, password, port, use_ssl, use_tls, sender, None,
    )
    message = Message(subject, recipients, html=html, sender=sender)
    with mail_client.connect() as connect:
        message.send(connect)

def send_email_message(message: Message):
    env: str = os.getenv("FLASK_ENV") or "develop"
    config = configInfo[env]
    if not config:
        return
    server: str = getattr(config, "MAIL_SERVER")
    port: int = getattr(config, "MAIL_PORT")
    use_ssl: bool = getattr(config, "MAIL_USE_SSL")
    use_tls: bool = getattr(config, "MAIL_USE_TLS")
    username: str = getattr(config, "MAIL_USERNAME")
    password: str = getattr(config, "MAIL_PASSWORD")
    sender: str = message.sender or getattr(config, "MAIL_DEFAULT_SENDER")
    if not message.sender:
        message.sender = sender

    mail_client = Mail(
        server, username, password, port, use_ssl, use_tls, sender, None,
    )
    mail_client.send(message)
    