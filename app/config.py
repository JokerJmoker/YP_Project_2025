import os

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
    
class DevelopmentConfig(Config):
    USE_MIGRATIONS = False  # Использует create_all()

class ProductionConfig(Config):
    USE_MIGRATIONS = True   # Полагается на миграции