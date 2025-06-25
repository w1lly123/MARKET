# 檔案: market/__init__.py (最終正確版本)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config
from flask_jwt_extended import JWTManager, get_jwt_identity, get_jwt

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化擴充套件
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # 註冊藍圖
    # 【注意】這裡導入的是 routes.py，請確保您的路由檔名正確
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # 註冊內容處理器，讓所有模板都能存取 current_user
    @app.context_processor
    def inject_user():
        try:
            identity = get_jwt_identity()
            if identity:
                claims = get_jwt()
                return dict(
                    current_user={
                        "id": identity,
                        "is_admin": claims.get("is_admin"),
                        "nickname": claims.get("nickname")
                    }
                )
        except Exception:
            pass
        return dict(current_user=None)

    return app