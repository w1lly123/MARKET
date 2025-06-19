# market/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config  # <-- 注意這裡的點

# 先建立擴充套件的實例，但先不初始化
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    """
    這就是應用程式工廠函式
    """
    app = Flask(__name__)
    
    # 從設定物件中載入設定
    app.config.from_object(config_class)

    # 【關鍵】將擴充套件的實例與 app 綁定
    db.init_app(app)
    migrate.init_app(app, db)

    # --- 這裡註冊您的路由 ---
    # 為了避免循環導入，我們在函式內部導入路由
    
    # --- 註冊藍圖 ---
    # 從 routes.py 導入我們建立的 main 這個藍圖物件
    from .routes import main as main_blueprint
    # 將這個藍圖註冊到 app 上
    app.register_blueprint(main_blueprint)

    return app