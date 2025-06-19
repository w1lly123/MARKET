# config.py (整合 PostgreSQL 與安全性的建議版本)

import os
from dotenv import load_dotenv

# 獲取專案的根目錄
basedir = os.path.abspath(os.path.dirname(__file__))

# 載入 .env 檔案中的環境變數
# 這樣我們就可以把敏感資訊放在 .env 檔案中，而不是直接寫在程式碼裡
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """
    統一的應用程式設定
    """
    # 1. SECRET_KEY 的安全設定
    # 優先從環境變數中讀取 SECRET_KEY，如果沒有，則使用一個預設的、難以猜測的字串
    # 這樣在正式部署時，我們可以在主機上設定這個環境變數，增加安全性
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-hard-to-guess-string-for-dev'

    # 2. 資料庫設定
    # 關閉 Flask-SQLAlchemy 的事件通知系統，可減少記憶體使用
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 3. PostgreSQL 資料庫連線 URI 的安全設定
    # 同樣地，優先從環境變數 'DATABASE_URL' 讀取完整的連線字串
    # 如果沒有，再使用您提供的本地端設定作為開發時的預設值
    DB_USERNAME = os.environ.get('DB_USERNAME') or "postgres"
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or "root"
    DB_HOST = os.environ.get('DB_HOST') or "localhost"
    DB_PORT = os.environ.get('DB_PORT') or "5432"
    DB_NAME = os.environ.get('DB_NAME') or "ecommerce"
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"