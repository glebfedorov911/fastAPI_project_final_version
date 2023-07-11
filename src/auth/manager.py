from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin

from src.auth.models import User, get_user_db

from src.config import SECRET, SMTP_USER, SMTP_PASS, REDIS_HOST, REDIS_PORT

import smtplib
from email.message import EmailMessage

from celery import Celery

celery = Celery("tasks", broker=f"redis://{REDIS_HOST}:{REDIS_PORT}")

class UserManager(UUIDIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(
        self, user: User, request: Optional[Request] = None
    ) -> None:
        email = SendingEmail("Регистрация", user, f"Пользователь {user.id} зарегистрирован")
        email.send_email(email)

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ) -> None:
        email = SendingEmail("Восстановление пароля", user, f"<h1>Здравствуйте!</h1> ваш токен: <b>{token}</b>")
        email.send_email(email)

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

class SendingEmail:
    SMTP_HOST = "smtp.gmail.com"
    SMTP_PORT = 465
    SMTP_USER = SMTP_USER
    SMTP_PASS = SMTP_PASS

    def __init__(self, subject: str, user: User, msg: str):
        self.subject = subject
        self.user = user
        self.msg = msg

    def email_message(self):
        email = EmailMessage()
        email["Subject"] = self.subject
        email["From"] = SMTP_USER
        email["To"] = self.user.email

        email.set_content(
            self.msg,
            subtype="html"
        )

        return email

    @celery.task
    def send_email(self):
        self.email = self.email_message()
        with smtplib.SMTP_SSL(self.SMTP_HOST, self.SMTP_PORT) as server:
            server.login(self.SMTP_USER, self.SMTP_PASS)
            server.send_message(self.email)