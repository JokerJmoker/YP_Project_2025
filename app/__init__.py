# точка входа(функция по созданию приложения)
from flask import Flask
from .extensions import db, migrate, login_manager, assets
from .config import Config
from .bundles import bundles, register_bundles

from .routes.user import user
from .routes.post import post
from .routes.configurator import configurator
from .routes.components import components


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    app.register_blueprint(user)
    app.register_blueprint(post)
    app.register_blueprint(configurator)
    app.register_blueprint(components)

    
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
    
    from .models import (CaseFan, CpuCooler, Cpu, Post, SoDimm, User, 
                         Dimm, Gpu, Hdd_2_5, hdd_3_5, Motherboard, PcCase,
                         PowerSupply, SsdM2, Ssd, WaterCooling
    )
    
    with app.app_context():
        if app.config.get('USE_MIGRATIONS', False):
            # Режим с миграциями - ничего не создаём
            pass
        else:
            # Режим разработки - создаём таблицы, если их нет
            try:
                db.create_all()
            except Exception as e:
                app.logger.warning(f"Could not create tables: {e}")
    
    return app
