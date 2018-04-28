import secrets
import hmac
import hashlib
import base64
from datetime import datetime, timedelta
import bcrypt
from sqlalchemy.sql import exists

from app import db
from app import ma
<<<<<<< HEAD
from models.ag import AG, AGSchema
=======
from models.ag import AG
from models.date import Date
import bcrypt
>>>>>>> 9ee87f146c7ad81d480cad54f686413f2f3dabaa

from models.associations import UserAG, DateUser


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    username = db.Column(db.String(16), unique=True, nullable=False)
    email = db.Column(db.String(48), unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)

    ags = db.relationship(AG, secondary="user_ag_association")

    #dates = db.relationship(Date, secondary="user_date_asscociation")

    sessions = db.relationship("Session", backref='persons', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12))

    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password)


class UserSchema(ma.Schema):
    ags = ma.Nested(AGSchema, many=True, exclude=('users',))

    class Meta:
        fields = ('id', 'username', "ags")


class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    uid = db.Column(db.Integer, db.ForeignKey("users.id"))
    expires = db.Column(db.DateTime, nullable=False)
    token = db.Column(db.String(64), nullable=False)
    public_token = db.Column(db.String(16), unique=True, nullable=False)
    authenticated = db.Column(db.Boolean, default=False)
    revoked = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, user: User = None, days=60):
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
        """
        Generate a custom string cookie that includes both the public as well as the private token.
        :return: Cookie string
        """
        dig = hmac.new(b'a_perfect_secret', msg=self.token.encode('utf-8'), digestmod=hashlib.sha256).digest()
        str_dig = base64.b64encode(dig).decode()
        return f'{self.public_token}+{str_dig}'

    @staticmethod
    def verify(cookie: str):
        """
        Check if the provided cookie is part of a valid session.
        :param cookie: String cookie: "public_token+hash(token)"
        :return: a Session object when the session cookie was valid, False if
            the session cookie was invalid
        """
        if cookie:
            # get public token from cookie string
            pub = cookie.split("+")[0]
            # check if a session with the public token exists
            if db.session.query(exists().where(Session.public_token == pub)).scalar():
                # get the session from the db
                session = Session.query.filter_by(public_token=pub).scalar()
                if session.expires > datetime.now() and not session.revoked:
                    if secrets.compare_digest(session.get_string_cookie(), cookie):
                        return session

        return False


def __repr__(self):
    return f'<Session {self.id}>'
