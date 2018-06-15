from functools import wraps

from flask import g, redirect, url_for, request
from sqlalchemy import exists, and_, or_
from app.models import db
from app.models.ag import AG, AGMessage
from app.models.associations import UserAG, UserAGMessage
from app.models.user import User

from werkzeug.exceptions import Unauthorized, NotFound, BadRequest, Forbidden


def requires_auth():
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not g.session.authenticated:
                return redirect(url_for('auth.login_get', next=request.url))
            else:
                return f(*args, **kwargs)

        return wrapped

    return wrapper


def after_this_request(f):
    if not hasattr(g, 'after_request_callbacks'):
        g.after_request_callbacks = []
    g.after_request_callbacks.append(f)
    return f


def requires_existing_ag():
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            ag_name = kwargs.get('ag_name', None)
            ag_id = kwargs.get('ag_id', None)
            if db.session.query(exists().where(AG.id == ag_id)).scalar() and ag_id is not None:
                ag: AG = AG.query.filter_by(id=ag_id).scalar()

            elif db.session.query(exists().where(AG.name == ag_name)).scalar() and ag_name is not None:
                ag: AG = AG.query.filter_by(name=ag_name).scalar()
            else:
                return NotFound(description='AG could not be found')
            kwargs.setdefault('ag', ag)
            return f(*args, **kwargs)

        return wrapped

    return wrapper


def requires_ag():
    def wrapper(f):
        @wraps(f)
        @requires_existing_ag()
        def wrapped(*args, **kwargs):
            ag_name = kwargs.get('ag_name', None)
            ag_id = kwargs.get('ag_id', None)
            if ag_id is not None:
                ag: AG = AG.query.filter_by(id=ag_id).scalar()
            elif ag_name is not None:
                ag: AG = AG.query.filter_by(name=ag_name).scalar()
            else:
                return NotFound(description='AG could not be found')
            kwargs.setdefault('ag', ag)
            return f(*args, **kwargs)

        return wrapped

    return wrapper


def requires_gracefully_not_member():
    def wrapper(f):
        @wraps(f)
        @requires_ag()
        def wrapped(*args, **kwargs):
            ag = kwargs.get('ag')
            if not db.session.query(exists().where(
                    and_(UserAG.user_id == g.session.user_id, UserAG.ag_id == ag.id))).scalar() or db.session.query(
                    exists().where(
                            and_(UserAG.user_id == g.session.user_id, UserAG.ag_id == ag.id, UserAG.role == 'NONE",
                                 or_(UserAG.status == "LEFT", UserAG.status == "DECLINED")))).scalar():
                return f(*args, **kwargs)
            else:
                return BadRequest(description='you already have some kind of relation to this AG')

        return wrapped

    return wrapper


def requires_not_member():
    def wrapper(f):
        @wraps(f)
        @requires_ag()
        def wrapped(*args, **kwargs):
            ag = kwargs.get('ag')
            if not db.session.query(
                    exists().where(and_(UserAG.user_id == g.session.user_id, UserAG.ag_id == ag.id))).scalar():
                return f(*args, **kwargs)
            else:
                return BadRequest(description='you already have some kind of relation to this AG')

        return wrapped

    return wrapper


def requires_member():
    def wrapper(f):
        @wraps(f)
        @requires_ag()
        def wrapped(*args, **kwargs):
            ag = kwargs.get('ag')
            if db.session.query(
                    exists().where(and_(UserAG.user_id == g.session.user_id, UserAG.ag_id == ag.id))).scalar():
                return f(*args, **kwargs)
            else:
                return Unauthorized()

        return wrapped

    return wrapper


def requires_member_association():
    def wrapper(f):
        @wraps(f)
        @requires_member()
        def wrapped(*args, **kwargs):
            ag = kwargs.get('ag')
            user_ag = UserAG.query.filter_by(user_id=g.session.user_id, ag_id=ag.id).scalar()
            kwargs.setdefault('user_ag', user_ag)
            return f(*args, **kwargs)

        return wrapped

    return wrapper


def requires_membership():
    def wrapper(f):
        @wraps(f)
        @requires_member()
        def wrapped(*args, **kwargs):
            ag = kwargs.get('ag')
            user_ag = UserAG.query.filter_by(user_id=g.session.user_id, ag_id=ag.id).scalar()
            if (user_ag.role != 'NONE'):
                kwargs.setdefault('user_ag', user_ag)
                return f(*args, **kwargs)
            else:
                return Unauthorized()

        return wrapped

    return wrapper


def requires_mentor():
    def wrapper(f):
        @wraps(f)
        @requires_membership()
        def wrapped(*args, **kwargs):
            user_ag = kwargs.get('user_ag')
            if user_ag.role == 'MENTOR':
                return f(*args, **kwargs)
            else:
                return Unauthorized(description='you need to be mentor')

        return wrapped

    return wrapper

def requires_ag_message():
    def wrapper(f):
        @wraps(f)
        @requires_membership()
        def wrapped(*args, **kwargs):
            message_id = kwargs.get('message_id')
            if message_id:
                ag_message = db.session.query(AGMessage).filter_by(id = message_id).scalar()
                if ag_message:
                    kwargs.setdefault('ag_message', ag_message)
                    return f(*args, **kwargs)
                else:
                    return NotFound(description='not able to locate any message with this id')
            else:
                return BadRequest(description='you have not specified any message id')

        return wrapped

    return wrapper

def requires_ag_message_rights():
    def wrapper(f):
        @wraps(f)
        @requires_membership()
        @requires_ag_message()
        def wrapped(*args, **kwargs):
            ag_message = kwargs.get('ag_message')
            user_ag_message = db.session.query(UserAGMessage).filter_by(message_id = ag_message.id, user_id = g.session.user_id).scalar()
            if user_ag_message:
                kwargs.setdefault('user_ag_message', user_ag_message)
                return f(*args, **kwargs)
            else: 
                return Forbidden('you have no rights to read this message')

        return wrapped

    return wrapper

def get_membership(user_id, ag_id):
    user_ag = UserAG.query.filter_by(user_id=user_id, ag_id=ag_id).scalar()
    return user_ag


def get_ag_by_name(ag_name):
    ag = db.session.query(AG).filter_by(name=ag_name).scalar()
    return ag


def get_ag_by_id(ag_id):
    ag = db.session.query(AG).filter_by(id=ag_id).scalar()
    return ag


def get_user_by_username(username):
    user = db.session.query(User).filter_by(username=username).scalar()
    return user


def get_user_by_id(user_id):
    user = db.session.query(User).filter_by(id=user_id).scalar()
    return user