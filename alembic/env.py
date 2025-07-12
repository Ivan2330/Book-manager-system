import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# 🔁 додаємо app до PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.core.database import Base
from app.models import user, author, book

# 📄 конфіг Alembic
config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

# 🔊 логування
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 📦 метадані
target_metadata = Base.metadata


def run_migrations_online():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async def do_run_migrations():
        async with connectable.connect() as async_connection:
            def run_migrations(sync_connection):
                context.configure(
                    connection=sync_connection,
                    target_metadata=target_metadata,
                    compare_type=True,
                    compare_server_default=True,
                )
                with context.begin_transaction():
                    context.run_migrations()

            await async_connection.run_sync(run_migrations)

    asyncio.run(do_run_migrations())


run_migrations_online()
