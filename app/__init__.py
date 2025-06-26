from flask import Flask
from datetime import timedelta
from flask_session import Session  # Добавляем импорт для работы с сессиями
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
    
    # Инициализация расширений в правильном порядке
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Настройка сессий ДО инициализации login_manager
    app.config.update(
        SESSION_PERMANENT=True,
        PERMANENT_SESSION_LIFETIME=timedelta(hours=24),
        SESSION_USE_SIGNER=True,
        SESSION_COOKIE_SECURE=False if app.debug else True,  # HTTPS в production
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax'
    )
    Session(app)  # Инициализация системы сессий
    
    login_manager.init_app(app)
    assets.init_app(app)
    
    # Регистрация blueprint'ов
    app.register_blueprint(user)
    app.register_blueprint(post)
    app.register_blueprint(configurator)
    app.register_blueprint(components)
    
    # Настройка login_manager
    login_manager.login_view = 'user.login'
    login_manager.login_message = 'Для получения доступа к странице, необходимо сначала войти'
    login_manager.login_message_category = 'info'
    
    # Инициализация assets
    register_bundles(assets, bundles)
    
    # Инициализация хранилища конфигураций
    if not hasattr(app, 'pc_configurations'):
        app.pc_configurations = {}
    
    with app.app_context():
        if app.config.get('USE_MIGRATIONS', False):
            # Режим с миграциями - ничего не создаём явно
            pass
        else:
            # Режим разработки - создаём таблицы
            try:
                db.create_all()
                app.logger.info("Database tables created successfully")
            except Exception as e:
                app.logger.error(f"Could not create tables: {str(e)}")
                # В режиме разработки можно вывести более подробную ошибку
                if app.debug:
                    raise
    
    return app