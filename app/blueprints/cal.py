from flask import Blueprint, flash, g, redirect, render_template, url_for
from app.models.user import User, Session
from app import db
from app.utils import requires_auth
bp = Blueprint('cal', __name__)


@bp.route('/', methods=['GET'])
@requires_auth()
def get():

    return render_template('cal/index.html', title='Calendar')
