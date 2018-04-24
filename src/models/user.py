import secrets
import hmac
import hashlib
import base64
from datetime import datetime, timedelta

from app import db
from app import ma
from models.ag import AG
import bcrypt

import models.associations as ass


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    username = db.Column(db.String(250), unique=True, nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)

    ags = db.relationship("AG", secondary=ass.user_ag_association,
                          back_populates="users")

    sessions = db.relationship("Session", backref='persons', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12))

    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password)


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username')


class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    uid = db.Column(db.Integer, db.ForeignKey("users.id"))
    expires = db.Column(db.DateTime, nullable=False)
    token = db.Column(db.String, nullable=False)
    public_token = db.Column(db.String, unique=True, nullable=False)
    authenticated = db.Column(db.Boolean, default=False)
    revoked = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, user: User=None, days=60):
        if user:
            self.uid = user.id
            self.authenticated = True
        else:
            self.uid = None
            self.authenticated = False

        self.token = secrets.token_hex(64)
        self.public_token = secrets.token_hex(16)
        self.expires = datetime.today() + timedelta(days=days)

    def get_string_cookie(self):
        dig = hmac.new(b'a_perfect_secret', msg=self.token.encode('utf-8'), digestmod=hashlib.sha256).digest()
        str_dig = base64.b64encode(dig).decode()
        return f"{self.public_token}+{str_dig}"

    @staticmethod
    def verify(cookie: str):
        if cookie:
            pub = cookie.split("+")[0]
            session = Session.query.filter_by(public_token=pub).one()
            if session and session.expires > datetime.now():
                dig = hmac.new(b'a_perfect_secret', msg=session.token.encode('utf-8'), digestmod=hashlib.sha256).digest()
                str_dig = base64.b64encode(dig).decode()
                cookie_dig = cookie[cookie.index("+")+1:]
                if secrets.compare_digest(str_dig, cookie_dig):
                    return session

        return False

    def __repr__(self):
        return f"<Session {self.id}>"