# -*- coding: utf-8 -*-
from typing import Optional, List, ClassVar, Text, Dict, Set, Union, Tuple, Iterable
import os
import re
import smtplib
import unicodedata
from smtplib import SMTP
from email import charset, policy
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formatdate, formataddr, make_msgid, parseaddr
from time import time
from contextlib import contextmanager


def force_text(s: Union[str, bytes], encoding="utf-8", errors="strict") -> str:
    """
    Similar to smart_text, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if isinstance(s, str):
        return s

    try:
        if not isinstance(s, str):
            if isinstance(s, bytes):
                s = str(s, encoding, errors)
            else:
                s = str(s)
        else:
            s = s.decode(encoding, errors)
    except UnicodeDecodeError as e:
        raise e
    return s


def sanitize_subject(subject, encoding="utf-8") -> str:
    try:
        subject.encode("ascii")
    except UnicodeEncodeError:
        try:
            subject = Header(subject, encoding).encode()
        except UnicodeEncodeError:
            subject = Header(subject, "utf-8").encode()
    return subject


def sanitize_address(address: str, encoding="utf-8") -> str:
    addr: str
    nm: str
    if isinstance(address, str):
        t = parseaddr(force_text(address))
        nm, addr = t

    try:
        nm = Header(nm, encoding).encode()
    except UnicodeEncodeError:
        nm = Header(nm, "utf-8").encode()
    try:
        addr.encode("ascii")
    except UnicodeEncodeError:  # IDN
        if "@" in addr:
            localpart, domain = addr.split("@", 1)
            localpart = str(Header(localpart, encoding))
            domain = domain.encode("idna").decode("ascii")
            addr = "@".join([localpart, domain])
        else:
            addr = Header(addr, encoding).encode()
    return formataddr((nm, addr))


def sanitize_addresses(addresses: List[str], encoding="utf-8") -> Iterable[str]:
    return map(lambda e: sanitize_address(e, encoding), addresses)


def _has_newline(line) -> bool:
    """Used by has_bad_header to check for \\r or \\n"""
    if line and ("\r" in line or "\n" in line):
        return True
    return False


class Connection(object):
    mail: "Mail"
    number_emails: int

    """ Handles connections to hosts. """

    def __init__(self, mail):
        self.mail = mail

    def __enter__(self):
        # 调用 with 时 调用 __enter__
        self.host = self.configure_host()
        self.number_emails = 0
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if self.host:
            self.host.quit()

    def configure_host(self) -> Union[smtplib.SMTP, smtplib.SMTP_SSL]:
        host: Union[smtplib.SMTP, smtplib.SMTP_SSL]
        if self.mail.use_ssl:
            host = smtplib.SMTP_SSL(self.mail.server, self.mail.port)
        else:
            host = smtplib.SMTP(self.mail.server, self.mail.port)
        # host.set_debuglevel(1)
        if self.mail.username and self.mail.password:
            host.login(self.mail.username, self.mail.password)
        return host

    def send(self, message: "Message", envelop_from=None):
        """ 验证并发送 """
        assert message.send_to, "没有收件人"
        assert message.sender, "没有发件人"

        if not self.host:
            raise ValueError
        self.host.sendmail(
            message.sender, message.send_to, message.as_string(),
        )

        self.number_emails += 1

        if self.number_emails >= self.mail.max_emails:
            self.number_emails = 0
            self.host.quit()
            self.host = self.configure_host()

    def send_message(self, *args, **kwargs):
        self.send(*args, **kwargs)


class Attachment(object):
    """Encapsulates file attachment information.

    :versionadded: 0.3.5

    :param filename: filename of attachment
    :param content_type: file mimetype
    :param data: the raw file data
    :param disposition: content-disposition (if any)
    """

    def __init__(
        self,
        filename=None,
        content_type=None,
        data=None,
        disposition=None,
        headers=None,
    ):
        self.filename = filename
        self.content_type = content_type
        self.data = data
        self.disposition = disposition or "attachment"
        self.headers = headers or {}


class Message(object):
    """Encapsulates an email message.
    :param subject: email subject header
    :param body: plain text message
    :param recipients: recipients
    :param sender: email sender address
    :param date: send date
    :param charset: message character set
    :param extra_headers: A dictionary of additional headers for the message
    """

    subject: str
    _recipients: List[str]
    body: Optional[str]
    html: Optional[str]
    sender: Optional[str]
    _attachments: List[Attachment]  # 附件
    date: float
    _extra_headers: Dict[str, str]
    _mail_options: Dict[str, str]
    _msgId: str

    _charset: str = "utf-8"

    def __init__(
        self,
        subject: str = "",
        recipients: List[str] = [],
        body: Optional[str] = None,
        html: Optional[str] = None,
        sender: Optional[str] = None,
        attachments: Optional[List[Attachment]] = None,
        date: Optional[float] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        mail_options: Optional[Dict[str, str]] = None,
    ):
        self.subject = subject
        self._recipients = recipients or []
        self.sender = sender
        self.body = body
        self.html = html
        self.date = date or time()
        self._attachments = attachments or []
        self._extra_headers = extra_headers or {}
        self._mail_options = mail_options or {}
        self._msgId = make_msgid()

    @property
    def send_to(self) -> Set:
        return set(self._recipients)

    def _mimetext(self, text, subtype="plain") -> MIMEText:
        charset = self._charset
        message = MIMEText(text, _subtype=subtype, _charset=charset)
        return message

    def _message(self) -> Union[MIMEBase]:
        encoding = self._charset
        attachments = self._attachments
        message: MIMEBase
        if len(attachments) == 0 and not self.html:
            message = self._mimetext(self.body)
        elif len(attachments) > 0 and not self.html:
            message = MIMEMultipart()
            message.attach(self._mimetext(self.body))
        else:
            message = MIMEMultipart()
            alternative = MIMEMultipart("alternative")
            alternative.attach(self._mimetext(self.body, "plain"))
            alternative.attach(self._mimetext(self.html, "html"))
            message.attach(alternative)

        message["Subject"] = sanitize_subject(
            force_text(self.subject), encoding=encoding
        )
        message["From"] = sanitize_address(self.sender or "", encoding)
        message["To"] = ", ".join(
            list(set(sanitize_addresses(self._recipients, encoding)))
        )

        message["Date"] = formatdate(self.date, localtime=True)
        # see RFC 5322 section 3.6.4.
        message["Message-ID"] = self._msgId

        if self._extra_headers:
            for k, v in self._extra_headers.items():
                message[k] = v

        SPACES = re.compile(r"[\s]+", re.UNICODE)
        for attachment in attachments:
            f = MIMEBase(*attachment.content_type.split("/"))
            f.set_payload(attachment.data)
            encode_base64(f)

            filename = attachment.filename
            
            try:
                filename and filename.encode("ascii")
            except UnicodeEncodeError:
                filename = ("UTF8", "", filename)

            f.add_header(
                "Content-Disposition", attachment.disposition, filename=filename
            )

            for key, value in attachment.headers:
                f.add_header(key, value)

            message.attach(f)

        return message

    def as_string(self):
        return self._message().as_string()

    def as_bytes(self):
        return self._message().as_bytes()

    def __str__(self):
        return self.as_string()

    def __bytes__(self):
        return self.as_bytes()

    def send(self, connection: Connection):
        connection.send(self)

    def add_recipient(self, recipient: str):
        self._recipients.append(recipient)

    def has_bad_headers(self) -> bool:
        headers = self._recipients
        if self.sender:
            headers.append(self.sender)
        for header in headers:
            if _has_newline(header):
                return True

        if self.subject:
            if _has_newline(self.subject):
                for linenum, line in enumerate(self.subject.split("\r\n")):
                    if not line:
                        return True
                    if linenum > 0 and line[0] not in "\t ":
                        return True
                    if _has_newline(line):
                        return True
                    if len(line.strip()) == 0:
                        return True
        return False

    def attach(
        self,
        filename: Optional[str] = None,
        content_type: Optional[str] = None,
        data: Optional[bytes] = None,
        disposition: Optional[str] = None,
        headers: Dict[str, str] = {},
    ):
        self._attachments.append(
            Attachment(filename, content_type, data, disposition, headers)
        )


class Mail(object):
    server: str
    username: str
    password: str
    port: int
    use_ssl: bool
    use_tls: bool
    sender: str
    max_emails: int

    def __init__(
        self,
        server: str,
        username: str,
        password: str,
        port: int,
        use_ssl: bool,
        use_tls: bool,
        sender: str,
        max_emails: Optional[int],
    ):
        self.server = server
        self.username = username
        self.password = password
        self.port = port
        self.use_ssl = use_ssl or False
        self.use_tls = use_tls or False
        self.sender = sender
        self.max_emails = max_emails or 3

    def connect(self) -> Connection:
        return Connection(self)

    def send(self, message: Message):
        with self.connect() as connection:
            message.send(connection)

    def send_message(self, *args, **kwargs):
        self.send(Message(*args, **kwargs))
