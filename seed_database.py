# seed_database.py

from market import create_app, db
from market.models import Product

app = create_app()

# 這裡是我們要新增的範例商品資料
product_data = [
    # 1. BTS
    {
        'name': "BTS - Love Yourself 結 'Answer'",
        'price': 850.00,
        'description': "K-POP天團防彈少年團的經典Repackage專輯，收錄多首熱門主打。內含寫真書、隨機小卡、CD等豐富內容。",
        'image_url': 'https://i.imgur.com/v2REEdy.jpg'
    },
    # 2. BLACKPINK
    {
        'name': "BLACKPINK - BORN PINK (Box Set Ver.)",
        'price': 920.00,
        'description': "全球知名女團BLACKPINK的第二張正規專輯，展現獨特Girl Crush魅力。豪華盒裝版，粉絲必備收藏。",
        'image_url': 'https://i.imgur.com/A65V73w.jpg'
    },
    # 3. NewJeans
    {
        'name': "NewJeans - 2nd EP 'Get Up' (Bunny Beach Bag ver.)",
        'price': 780.50,
        'description': "引領潮流的大勢女團NewJeans第二張迷你專輯，清爽夏日風格。附贈超可愛的兔子沙灘包及多樣特典。",
        'image_url': 'https://i.imgur.com/uR1jj5c.jpg'
    },
    # 4. Stray Kids
    {
        'name': "Stray Kids - ★★★★★ (5-STAR)",
        'price': 880.00,
        'description': "Stray Kids的第三張正規專輯，以強烈的音樂風格和自主創作能量席捲全球，展現五星級的舞台魅力。",
        'image_url': 'https://i.imgur.com/sYnO3iU.jpg'
    },
    # 5. IU
    {
        'name': "IU - 5th Album 'LILAC'",
        'price': 750.00,
        'description': "國民天后IU的第五張正規專輯，以「丁香花」為主題，紀念20代的最後並迎接新的開始，風格多變成熟。",
        'image_url': 'https://i.imgur.com/0uGzT6a.jpg'
    },
    # 6. SEVENTEEN
    {
        'name': "SEVENTEEN - 10th Mini Album 'FML'",
        'price': 820.00,
        'description': "人氣男團SEVENTEEN的第十張迷你專輯，以雙主打曲展現多樣面貌，傳遞克服困境、積極向前的正能量。",
        'image_url': 'https://i.imgur.com/o2xJqG1.png'
    },
    # 7. LE SSERAFIM
    {
        'name': "LE SSERAFIM - 1st Studio Album 'UNFORGIVEN'",
        'price': 890.00,
        'description': "無畏前行的LE SSERAFIM首張正規專輯，融合西部風格與流行元素，展現不被定義、開拓自身道路的帥氣形象。",
        'image_url': 'https://i.imgur.com/Yg0gL2W.jpg'
    },
    # 8. IVE
    {
        'name': "IVE - I've IVE (1st Album)",
        'price': 870.00,
        'description': "新生代代表女團IVE的首張正規專輯，以充滿自信的音樂和視覺效果，鞏固其獨特的音樂色彩和世界觀。",
        'image_url': 'https://i.imgur.com/lJ4jE6K.jpg'
    },
    # 9. TWICE
    {
        'name': "TWICE - Formula of Love: O+T=<3",
        'price': 910.00,
        'description': "亞洲第一女團TWICE的第三張正規專輯，成員們親自參與多首歌曲創作，以多樣的曲風探索愛情的各種公式。",
        'image_url': 'https://i.imgur.com/0y7E2F8.jpg'
    },
    # 10. (G)I-DLE
    {
        'name': "(G)I-DLE - 6th Mini Album 'I feel'",
        'price': 760.00,
        'description': "概念女王(G)I-DLE的第六張迷你專輯，以Y2K復古風格和充滿自信的歌曲，探討自尊與自我認同的核心主題。",
        'image_url': 'https://i.imgur.com/T0a3X8u.jpg'
    }
]

def seed_data():
    """一個用來清除並重新填充資料庫的函式"""
    with app.app_context():
        # 刪除所有現有的資料表
        print("正在刪除所有資料表...")
        db.drop_all()
        print("資料表刪除完畢。")

        # 根據 models.py 重新建立所有資料表
        print("正在根據模型建立新資料表...")
        db.create_all()
        print("新資料表建立完畢。")

        # 新增範例商品資料
        print("正在新增 K-POP 專輯範例資料...")
        for item in product_data:
            # 建立 Product 物件實例
            product = Product(
                name=item['name'],
                price=item['price'],
                description=item['description'],
                image_url=item['image_url'],
                quantity=100  # 假設所有專輯的初始庫存都是 100
            )
            # 將物件加入到 session 中
            db.session.add(product)
        
        # 一次性提交所有變更到資料庫
        db.session.commit()
        print("範例資料新增成功！")
        
        # --- 【新增的驗證步驟】 ---
        print("\n--- 開始驗證資料庫 ---")
        try:
            product_count = Product.query.count()
            print(f"驗證成功：在資料庫中找到 {product_count} 筆商品資料。")
            if product_count > 0:
                first_product = Product.query.first()
                print(f"第一筆商品是：{first_product.name}")
        except Exception as e:
            print(f"驗證失敗：查詢資料庫時發生錯誤: {e}")
        print("---------------------\n")

if __name__ == '__main__':
    seed_data()