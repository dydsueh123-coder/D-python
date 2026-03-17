from flask import Blueprint

surveys_bp = Blueprint('surveys', __name__)

from . import routes  # noqa
