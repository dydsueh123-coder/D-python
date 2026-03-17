from flask import Blueprint

recordings_bp = Blueprint('recordings', __name__)

from . import routes  # noqa
