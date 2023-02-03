import os

class Config:
    SECRET_KEY = "asndd8377"
    SQLALCHEMY_DATABASE_URI = "sqlite:///myproject.db"
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("EMAIL_USER")
    MAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")