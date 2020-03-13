from typing import List, Union
import os
from flask import render_template
from flask_mail import Message
from app.utils import get_logger
from app.utils import mail_client
from app.utils import celery_app
from app import create_app

logger = get_logger(__file__)


@celery_app.task(name="web_task.send_email")
def send_email(recipient: str, subject: str, template: str, **kwargs):
    app = create_app(os.getenv("FLASK_ENV") or "default")
    with app.app_context():
        message = Message(
            subject=app.config["MAIL_SUBJECT_PREFIX"] + " " + subject,
            sender=app.config["MAIL_USERNAME"],
            recipients=[recipient],
        )
        logger.info(str(app.config["MAIL_USERNAME"]))
        logger.info(str(app.config["MAIL_DEBUG"]))
        # message.body = render_template(template + '.txt', **kwargs)
        message.html = render_template(template + '.html', **kwargs)
        mail_client.send(message)

