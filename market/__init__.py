from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config
from flask_jwt_extended import JWTManager, get_jwt_identity, get_csrf_token


db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    """
    應用程式工廠，用於建立和設定 Flask 應用實例。
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化擴充套件
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from .models import User 
    # --- 內容處理器 (Context Processors) ---
    # 透過它們注入的變數，可以在所有 Jinja2 模板中直接使用。

    @app.context_processor
    def inject_current_user():
        """
        注入當前登入的使用者物件。
        如果使用者未登入，則 current_user 為 None。
        """
        try:
            identity = get_jwt_identity()
            if identity:
                # 從資料庫中查詢完整的使用者物件
                user = db.session.get(User, identity)
                return dict(current_user=user)
        except Exception:
            # 在沒有請求上下文或 JWT 無效時，靜默處理
            pass
        return dict(current_user=None)

    @app.context_processor
    def inject_csrf_token():
        """
        注入 CSRF Token，方便在 AJAX 和表單中使用。
        """
        try:
            # 必須在有 access_token_cookie 的情況下才能生成 CSRF Token
            encoded_token = request.cookies.get('access_token_cookie')
            if encoded_token:
                return dict(csrf_token=get_csrf_token(encoded_token))
        except Exception:
            pass
        return dict(csrf_token=None)


    # --- 註冊藍圖 ---
    # 確保在函式內部導入，避免循環依賴
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app