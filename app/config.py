import os
from datetime import timedelta

class Config(object):
    APPNAME = 'app'
    ROOT = os.path.abspath(APPNAME)
    UPLOAD_PATH = '/static/upload/'
    SERVER_PATH = ROOT + UPLOAD_PATH
    
    USER = os.environ.get('POSTGRESS_USER', 'jokerjmoker')
    PASSWORD = os.environ.get('POSTGRESS_PASSWORD', '270961Ts')
    HOST = os.environ.get('POSTGRESS_HOST', '127.0.0.1')
    PORT =os.environ.get('POSTGRESS_PORT', '5532')
    DB = os.environ.get('POSTGRESS_DB', 'mydb')
    
    SQLALCHEMY_DATABASE_URI = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}'
    SECRET_KEY = 'hihihihihahahahah'
    SQLALCHEMY_TRACK_MODIFICATIONS = 'True'
    
    # Настройки сессии
    SECRET_KEY = os.environ.get('SECRET_KEY', 'hihihihihahahahah')  
    SESSION_TYPE = 'filesystem'  # Хранить сессии на файловой системе (временное решение)
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_USE_SIGNER = True  # Подписывать cookie для безопасности
    SESSION_COOKIE_NAME = 'pc_configurator_session'
    SESSION_COOKIE_SECURE = False  # True только для HTTPS в продакшене
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
class DevelopmentConfig(Config):
    USE_MIGRATIONS = False  # Использует create_all()

class ProductionConfig(Config):
    USE_MIGRATIONS = True   # Полагается на миграции