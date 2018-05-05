from datetime import date

from sqlalchemy.sql import exists
from werkzeug.exceptions import NotFound
from flask import Blueprint, jsonify, g

import utils

from app import db

from models.associations import UserAG
from models.date import Date, DateSchema

bp = Blueprint("date_api", __name__)

date_schema = DateSchema()
dates_schema = DateSchema(many=True)


@bp.route("/id/<date_id>", methods=["GET"])
@utils.requires_auth()
def get_date_by_id(date_id):
    """
        Query an AG specified by its id
        :param ag_id: A specific id
        :return: JSON representation of the AG
        """
    if db.session.query(exists().where(Date.id == date_id)).scalar():
        date_obj = Date.query.get(date_id).scalar()
        if db.session.query(exists().where(UserAG.user_id == g.session.user_id and UserAG.ag_id == ag_id)).scalar():
            return ag_schema_intern.jsonify(ag), 200
        else:
            return ag_schema.jsonify(ag), 200
    else:
        return NotFound()

@bp.route("/name/<date_name>", methods=["GET"])
def get_date_by_date(date_name):
    odate = date(int(date_name[4:]), int(date_name[2:4]), int(date_name[:2]))
    fdate = Date.query.filter_by(day=odate).scalar()
    return date_schema.jsonify(fdate)


@bp.route("/", methods=["GET"])
def get_all_dates():
    all_dates = Date.query.all()
    result = date_schema.dump(all_dates)
    return jsonify(result)
