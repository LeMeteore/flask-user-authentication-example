from . import db
import datetime
import uuid
import jwt  # type:ignore
from werkzeug.security import (  # type:ignore
    generate_password_hash, check_password_hash
)


class User(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    pubid = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String(100))
    active = db.Column(db.Boolean, default=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password_hash = generate_password_hash(kwargs.get('password'))
        self.pubid = str(uuid.uuid4())

    def save(self):
        db.session.add(self)
        db.session.commit()

    @property
    def password(self):
        raise AttributeError("password is not readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_active(self):
        return self.active

    def activate(self):
        self.active = True

    def is_admin(self):
        return True

    def generate_token(self, minutes=3):
        from flask import current_app as app  # type:ignore
        content = {
            'pubid' : self.pubid,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes)
        }
        token = jwt.encode(
            content, app.config['SECRET_KEY']
        )
        return token

    @staticmethod
    def verify_token(token):
        from flask import current_app as app  # type:ignore
        try:
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=['HS256']
            )
        except jwt.exceptions.InvalidSignatureError as e:
            raise e
        except jwt.exceptions.ExpiredSignatureError as e:
            raise e
        current_user = User.query.filter_by(pubid=data['pubid']).first()
        return current_user
