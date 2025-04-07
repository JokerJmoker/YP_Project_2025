# точка входа(функция по созданию приложения)
from flask import Flask
from .extensions import db, migrate, login_manager, assets
from .config import Config
from .bundles import bundles, register_bundles

from .routes.user import user
from .routes.post import post


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    app.register_blueprint(user)
    app.register_blueprint(post)
    

    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    assets.init_app(app)
    
    #Login_manager
    login_manager.login_view = 'user.login'
    login_manager.login_message = 'Для получения доступа к странице, необходимо сначала войти'
    login_manager.login_message_category = 'info'
    
    #Assets
    register_bundles(assets, bundles)
    
    
    with app.app_context():
        db.create_all()
        
    return app 