import os
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-hard-to-guess-string-for-dev'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # --- PostgreSQL 設定 ---
    DB_USERNAME = os.environ.get('DB_USERNAME') or "postgres"
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or "root"
    DB_HOST = os.environ.get('DB_HOST') or "localhost"
    DB_PORT = os.environ.get('DB_PORT') or "5432"
    DB_NAME = os.environ.get('DB_NAME') or "ecommerce"
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # --- JWT 設定 ---
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'a-super-secret-jwt-key-for-dev'
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = False  # 開發環境 (http) 必須為 False
    JWT_COOKIE_SAMESITE = "Lax" # 指定 SameSite 策略
    JWT_CSRF_IN_COOKIES = True # 啟用 CSRF 保護
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_CSRF_CHECK_FORM = True
    
    # 綠界金流設定 (從環境變數讀取更佳)
    ECPAY_MERCHANT_ID = os.environ.get('ECPAY_MERCHANT_ID', '3002599') # 請替換為您的測試商店代號
    ECPAY_HASH_KEY = os.environ.get('ECPAY_HASH_KEY', 'spPjZn66i0OhqJsQ') # 請替換為您的 HashKey
    ECPAY_HASH_IV = os.environ.get('ECPAY_HASH_IV', 'hT5OJckN45isQTTs') # 請替換為您的 HashIV
    ECPAY_API_URL = "https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5" # 綠界測試環境 URL
    
config = {
    'development': Config,
    'production': Config,
    'default': Config
}