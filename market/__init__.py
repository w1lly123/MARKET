import os
from flask import Flask, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, get_jwt_identity, get_csrf_token, verify_jwt_in_request
from config import config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # --- 註冊藍圖 (Blueprints) ---
    from .routes.auth_route import auth_bp
    from .routes.product_route import product_bp
    from .routes.order_route import order_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(product_bp)
    app.register_blueprint(order_bp, url_prefix='/order')
    
    from . import models

    # --- 內容處理器 (Context Processor) ---
    @app.context_processor
    def inject_user_and_csrf():
        """
        將當前登入的使用者物件 (current_user) 和 CSRF 權杖 (csrf_token)
        注入到所有模板中，方便直接使用。
        """
        from .models import User

        # 使用 verify_jwt_in_request(optional=True)
        # 這個函式會溫和地檢查請求中是否有 JWT。
        # 如果有，後續的 get_jwt_identity() 就能安全執行。
        # 如果沒有（例如在公開頁面），它也不會拋出錯誤。
        verify_jwt_in_request(optional=True)
        
        identity = get_jwt_identity()
        user = db.session.get(User, identity) if identity else None
        
        csrf = None
        # 只有在確認使用者已登入的情況下，才去嘗試取得 CSRF 權杖
        if identity:
            encoded_token = request.cookies.get('access_token_cookie')
            if encoded_token:
                csrf = get_csrf_token(encoded_token)
        
        return dict(current_user=user, csrf_token=csrf)

    return app