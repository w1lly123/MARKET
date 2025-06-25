# 檔案: market/config.py (最終正確版本)

import os
from dotenv import load_dotenv

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