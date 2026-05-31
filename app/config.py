import os

from dotenv import load_dotenv


load_dotenv()


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_COMPACT = True
    TESTING = False
    DEBUG = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL


config_by_env = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
}


def get_config():
    app_env = os.getenv("APP_ENV", "development").lower()
    return config_by_env.get(app_env, DevelopmentConfig)
