Flask K-POP 電商網站
這是一個使用 Python Flask 框架建構的全功能電子商務網站，專注於銷售 K-POP 相關專輯商品。專案採用了現代化的分層架構，並整合了台灣本地的金流服務，旨在提供一個穩固、可擴展且功能完整的電商解決方案。

主要功能
使用者認證系統:

完整的使用者註冊與登入流程。

使用 JWT (JSON Web Tokens) 搭配 Cookies 進行安全的 session 管理。

區分一般使用者與管理員 (Admin) 權限。

商品系統:

首頁商品列表展示。

商品詳情頁面。

後台管理: 管理員可新增、刪除商品。

購物車系統:

使用者可將商品加入購物車。

在購物車中可查看商品、調整數量（未來可擴充）、移除商品。

自動計算購物車總金額。

訂單與結帳系統:

完整的結帳流程，包含填寫配送地址。

金流串接: 整合綠界 (ECPay) 金流服務，支援信用卡等多元支付方式。

顧客訂單紀錄: 使用者可查看自己的歷史訂單列表與訂單詳情。

後台訂單查詢: 管理員可透過訂單編號或顧客 Email 查詢訂單。

技術棧 (Tech Stack)
後端:

框架: Flask

資料庫: PostgreSQL

ORM: SQLAlchemy

資料庫遷移: Flask-Migrate (Alembic)

認證: Flask-JWT-Extended

金流: 綠界 ECPay Python SDK (手動整合)

前端:

模板引擎: Jinja2

CSS 框架: Tailwind CSS

環境管理:

虛擬環境: venv

環境變數: python-dotenv

專案架構
本專案採用了可高度擴展的分層式架構，將不同職責的程式碼分離到獨立的模組中，以提升可維護性。

market/
├── controllers/    # 商業邏輯層：處理所有請求的詳細邏輯
├── models/         # 模型層：定義所有資料庫的結構 (ORM Models)
├── routes/         # 路由層：定義所有 URL 端點 (Blueprints)
├── templates/      # 視圖層：存放所有 HTML 模板
└── __init__.py     # 應用程式工廠：組裝所有模組

安裝與設定指南
請依照以下步驟在本機設定並執行此專案。

1. 前置需求
Python 3.11 (建議版本，以確保與 ecpay-payment-sdk 相容)

PostgreSQL 資料庫已安裝並正在運行

2. 建立專案環境
# 1. 複製此專案
git clone <your-repository-url>
cd <your-project-folder>

# 2. 建立並啟用 Python 3.11 虛擬環境
python3.11 -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. 安裝專案依賴
# (建議您先執行 pip freeze > requirements.txt 來產生依賴列表)
pip install -r requirements.txt

3. 設定環境變數
在專案根目錄下，建立一個名為 .env 的檔案，並填入以下內容：

# Flask
SECRET_KEY='your-flask-secret-key'
JWT_SECRET_KEY='your-jwt-secret-key'

# PostgreSQL 資料庫連線資訊
DB_USERNAME='your_db_user'
DB_PASSWORD='your_db_password'
DB_HOST='localhost'
DB_PORT='5432'
DB_NAME='ecommerce_dev'

# 綠界金流測試金鑰 (請至綠界開發者後台取得)
ECPAY_MERCHANT_ID='3002607'
ECPAY_HASH_KEY='pwFHCqoqZGmho4w6'
ECPAY_HASH_IV='EkRm7iFT261dpevs'

4. 設定資料庫
建立資料庫: 請在 PostgreSQL 中手動建立一個名為 ecommerce_dev 的資料庫。

執行資料庫遷移: 在終端機中，依序執行以下指令來建立所有資料表。

# 設定 FLASK_APP 環境變數
# Windows (CMD): set FLASK_APP=run.py
# macOS/Linux: export FLASK_APP=run.py

# 初始化遷移環境 (只需在第一次執行)
flask db init

# 產生遷移腳本
flask db migrate -m "Initial database schema"

# 將結構應用到資料庫
flask db upgrade

5. (選用) 填充範例資料
執行 seed 腳本來將範例商品資料加入到資料庫中。

python seed_database.py

6. 啟動應用程式
python run.py

現在，您可以在瀏覽器中打開 http://127.0.0.1:5000 來訪問您的網站了！

使用說明
如何建立管理員帳號
透過網站前端的註冊頁面，註冊一個普通帳號。

使用資料庫管理工具 (如 pgAdmin) 連接到您的資料庫。

找到 user 表格，將您剛剛註冊的使用者對應的 is_admin 欄位，從 false 修改為 true。

金流測試 (ECPay)
綠界金流的後端通知 (ReturnURL) 需要一個公開的網址才能接收。在本地開發時，您需要使用 ngrok 等工具來建立一個臨時的公開網址。

啟動 ngrok: ngrok http 5000

將 ngrok 產生的 Forwarding 網址，手動替換到 market/controllers/order_controller.py 中的 ReturnURL 參數。
