import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Flask 앱 임포트
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db

# Flask 앱 컨텍스트
flask_app = create_app(os.environ.get('FLASK_ENV', 'development'))

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 모델 메타데이터 (자동 마이그레이션용)
target_metadata = db.metadata


def run_migrations_offline() -> None:
    url = flask_app.config.get('SQLALCHEMY_DATABASE_URI')
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with flask_app.app_context():
        connectable = db.engine
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
            )
            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
