from os import getenv
from typing import Optional

from agno.storage.sqlite import SqliteStorage
from pydantic_settings import BaseSettings

def get_local_storage():
    return SqliteStorage(
        table_name="agent_sessions",
        db_file="db/data.db"
    )

class DbSettings(BaseSettings):
    """Database settings that can be set using environment variables.

    Reference: https://docs.pydantic.dev/latest/usage/pydantic_settings/
    """

    # Database configuration
    db_host: Optional[str] = None
    db_port: Optional[int] = None
    db_user: Optional[str] = None
    db_pass: Optional[str] = None
    db_database: Optional[str] = None
    db_driver: str = "postgresql+psycopg"
    # Create/Upgrade database on a startup using alembic
    migrate_db: bool = False

    def get_db_url(self) -> str:
        db_url = "{}://{}{}@{}:{}/{}".format(
            self.db_driver,
            self.db_user,
            f":{self.db_pass}" if self.db_pass else "",
            self.db_host,
            self.db_port,
            self.db_database,
        )

        # Use a local database if RUNTIME_ENV is not set
        if "None" in db_url and getenv("RUNTIME_ENV") is None:
            logger.debug("Using local database")
            db_url = "sqlite:///./agendev.db"

        logger.debug(f"Access to the database: {self.db_host} on ENV: {getenv("RUNTIME_ENV")}")
        if "None" in db_url or db_url is None:
            raise ValueError("Could not build database connection")
        return db_url


# Create DbSettings object
db_settings = DbSettings()
