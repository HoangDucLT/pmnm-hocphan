import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "doi-khoa-bi-mat-nay-khi-trien-khai")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(basedir, "nhasach.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Giới hạn dung lượng request (ảnh bìa tối đa 2 MB)
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(basedir, "app", "static", "uploads")
