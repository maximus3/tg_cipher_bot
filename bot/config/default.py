from pathlib import Path

from pydantic import BaseSettings, Field


class DefaultSettings(BaseSettings):
    """
    Default configs for application.

    Usually, we have three environments:
    for development, testing and production.
    But in this situation, we only have
    standard settings for local development.
    """

    ENV: str = Field('local', env='ENV')
    PROJECT_NAME: str = Field('PROJECT_NAME', env='PROJECT_NAME')
    DEBUG: bool = Field(True, env='DEBUG')

    TG_BOT_TOKEN: str = Field('', env='PROJECT_NAME')

    POSTGRES_DB: str = Field('data', env='POSTGRES_DB')
    POSTGRES_HOST: str = Field('localhost', env='POSTGRES_HOST')
    POSTGRES_USER: str = Field('pguser', env='POSTGRES_USER')
    POSTGRES_PORT: int = Field('5432', env='POSTGRES_PORT')
    POSTGRES_PASSWORD: str = Field('pgpswd', env='POSTGRES_PASSWORD')

    LOGGING_FORMAT = (
        '%(filename)s %(funcName)s [%(thread)d] '
        '[LINE:%(lineno)d]# %(levelname)-8s '
        '[%(asctime)s.%(msecs)03d] %(name)s: '
        '%(message)s'
    )
    LOGGING_FILE_DIR = Path('logs')
    LOGGING_APP_FILE = LOGGING_FILE_DIR / 'logfile.log'
    LOGGING_SCHEDULER_FILE = LOGGING_FILE_DIR / 'scheduler_logfile.log'

    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    CONFIG_FILENAME: str = 'config.yaml'

    @property
    def database_settings(self) -> dict[str, str | int]:
        """
        Get all settings for connection with database.
        """
        return {
            'database': self.POSTGRES_DB,
            'user': self.POSTGRES_USER,
            'password': self.POSTGRES_PASSWORD,
            'host': self.POSTGRES_HOST,
            'port': self.POSTGRES_PORT,
        }

    @property
    def database_uri(self) -> str:
        """
        Get uri for connection with database.
        """
        return (
            'postgresql+asyncpg://{user}:{password}@'
            '{host}:{port}/{database}'.format(
                **self.database_settings,
            )
        )

    @property
    def database_uri_sync(self) -> str:
        """
        Get uri for connection with database.
        """
        return (
            'postgresql://{user}:{password}@{host}:{port}/{database}'.format(
                **self.database_settings,
            )
        )

    class Config:
        env_file: Path | str = '.env'
        env_file_encoding = 'utf-8'
