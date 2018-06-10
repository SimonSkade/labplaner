from flask import Blueprint, g, redirect, render_template, url_for, flash
from sqlalchemy.sql import exists
from werkzeug.exceptions import NotFound, Unauthorized
from src.models.associations import UserAG
from src.models.ag import AG, AGSchema, AGSchemaIntern
from src.main import db
from src.utils import requires_auth, requires_mentor

from config.regex import ag_regex

bp = Blueprint('ag', __name__)

ag_schema = AGSchema()
ag_schema_intern = AGSchemaIntern()
ags_schema = AGSchema(many=True)


@bp.route('/add', methods=['GET'])
@requires_auth()
def create_ag():
    return render_template('ag/add.html', title='Create AG',
                                            ag_regex=ag_regex)


@bp.route('/<ag_name>', methods=['GET'])
@requires_auth()
def ag_dashboard(ag_name):
    if db.session.query(exists().where(AG.name == ag_name)).scalar():
        ag: AG = AG.query.filter_by(name=ag_name).scalar()
        if db.session.query(exists().where(UserAG.user_id == g.session.user_id and UserAG.ag_id == ag.id)).scalar():
            user_ag = UserAG.query.filter_by(user_id=g.session.user_id, ag_id=ag.id).scalar()
            if user_ag.role != 'NONE':
                schema = AGSchemaIntern()
                schema.context = {'ag_id': ag.id}
                return render_template('ag/dashboard.html', my_role='user_ag.role', ag=schema.dump(ag),
                                       title=ag.display_name)

        return Unauthorized()

    else:
        return NotFound()


@bp.route('/<ag_name>/invite', methods=['GET'])
@requires_auth()
def invite_ag(ag_name):

    if db.session.query(exists().where(AG.name == ag_name)).scalar():
        ag: AG = AG.query.filter_by(name=ag_name).scalar()
        if db.session.query(exists().where(UserAG.user_id == g.session.user_id and UserAG.ag_id == ag.id)).scalar():
            user_ag = UserAG.query.filter_by(user_id=g.session.user_id, ag_id=ag.id).scalar()
            if user_ag.role == 'MENTOR':
                return render_template('ag/invite.html', ag=ag_schema_intern.dump(ag),
                                       title=f'Invite {ag.display_name}')
        return Unauthorized()
    else:
        return NotFound()


# Events

@bp.route('/<ag_name>/event/add', methods=['GET'])
@requires_auth()
def create_event(ag_name):

    if db.session.query(exists().where(AG.name == ag_name)).scalar():
        ag: AG = AG.query.filter_by(name=ag_name).scalar()
        if db.session.query(exists().where(UserAG.user_id == g.session.user_id and UserAG.ag_id == ag.id)).scalar():
            user_ag = UserAG.query.filter_by(user_id=g.session.user_id, ag_id=ag.id).scalar()
            if user_ag.role == 'MENTOR':
                return render_template('ag/event/add.html', ag=ag_schema_intern.dump(ag),
                                       title=f'New Event {ag.display_name}')

        return Unauthorized()

    return NotFound()

@bp.route('/<ag_name>/settings', methods=['GET'])
@requires_auth()
def ag_settings(ag_name):
    if db.session.query(exists().where(AG.name == ag_name)).scalar():
        ag: AG = AG.query.filter_by(name=ag_name).scalar()
        if db.session.query(exists().where(UserAG.user_id == g.session.user_id and UserAG.ag_id == ag.id)).scalar():
            user_ag = UserAG.query.filter_by(user_id=g.session.user_id, ag_id=ag.id).scalar()
            if user_ag.role == 'MENTOR':
                return render_template('ag/settings.html', title='Create AG')
        return Unauthorized()
    else:
        return NotFound()