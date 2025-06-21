from flask import render_template, request, redirect, url_for, session, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User, Product
from datetime import datetime

main = Blueprint('main', __name__)

#首頁路由，從資料庫中提取商品資料並顯示
@main.route("/")
def home():
    products = Product.query.all()
    return render_template("home.html", products=products)
#錯誤路由，透過query string告知何種錯誤
@main.route("/error")
def error():
    msg = request.args.get("msg", "發生錯誤，請重新連線")
    return render_template("error.html", msg=msg)
#user註冊路由，首先判斷是否正確輸入所有欄位，再檢查email是否已被註冊過
#若皆沒問題則將使用者資料加入db，並以session暫存使用者資料後直接登入並導到首頁
@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    
    nickname = request.form.get("nickname")
    email = request.form.get("email")
    password = request.form.get("password")
    
    if not nickname or not email or not password:
        return redirect(url_for('main.error', msg="所有欄位皆為必填"))
        
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return redirect(url_for('main.error', msg="該信箱已被註冊"))
    hashed_password = generate_password_hash(password)
    new_user = User(nickname=nickname, email=email, password=hashed_password)
    
    db.session.add(new_user)
    db.session.commit()
    
    session["user_id"] = new_user.id
    session["nickname"] = new_user.nickname
    session["is_admin"] = new_user.is_admin
    
    return redirect(url_for('main.home'))

#登入頁路由，首先檢查欄位是否正確輸入，並檢查使用者資訊，若登入者為管理員則導到admin路由
@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    email = request.form.get("email")
    password = request.form.get("password")
    
    if not email or not password:
        return redirect(url_for('main.error', msg="信箱或密碼輸入錯誤"))
    
    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return redirect(url_for('main.login', msg="帳號或密碼錯誤"))
        
    session["user_id"] = user.id
    session["nickname"] = user.nickname
    session["is_admin"] = user.is_admin

    if user.is_admin:
        return redirect(url_for('main.admin'))
    else:
        return redirect(url_for('main.home'))

#登出路由，清除session，並導到主頁
@main.route("/logout")
def logout():
    # 修正點：使用 session.clear() 更簡潔
    session.clear()
    return redirect(url_for('main.home'))

#商品頁路由，透過url路徑接收商品id參數，並從資料庫中提取資料
@main.route("/product/<int:product_id>")
def product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return redirect(url_for('main.error', msg="找不到此商品"))
    return render_template("product.html", product=product)

#購物車路由，若使用者尚未登入則導至登入頁。從session中取得購物車商品，計算總進額並將資料傳遞到購物車頁面模板中
#******結帳頁尚未製作******
@main.route("/cart")
def cart():
    if "user_id" not in session:
        return redirect(url_for('main.login'))
    #定義一個cart_item變數存取在session中的 購物車商品
    cart_items = session.get("cart", [])
    #計算總金額
    total_price = sum(float(item["price"]) * item["quantity"] for item in cart_items)
    #導至購物車頁面並回傳商品以及總金額
    return render_template("cart.html", cart_items=cart_items, total_price=total_price)
#加入至購物車路由，首先檢查是否登入，從表單(POST方法)中取得商品id，以及數量(預設為1)
@main.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    if "user_id" not in session:
        return redirect(url_for('main.login'))

    product_id = request.form.get("product_id")
    quantity = int(request.form.get("quantity", 1))
    product = db.session.get(Product, product_id)

    if not product_id:
        return redirect(url_for('main.error', msg="未提供商品 ID"))

    if not product:
        return redirect(url_for('main.error', msg="找不到此商品"))
        
    cart = session.get("cart", [])
    
    found = False
    for item in cart:
        if str(item["id"]) == str(product.id):
            item["quantity"] += quantity
            found = True
            break
            
    if not found:
        # 【購物車修正】加入 name 和 image_url
        cart.append({
            "id": product.id,
            "name": product.name,
            "price": float(product.price),
            "quantity": quantity,
            "image_url": product.image_url
        })
        
    session["cart"] = cart
    return redirect(url_for('main.cart'))

#清除購物車路由，從session中取得cart裡的商品資料，用新列表覆蓋舊有的列表
#透過遍歷cart裡的item，若item['id']不等於item_id的話就保留
@main.route("/remove-from-cart/<int:item_id>")
def remove_from_cart(item_id):
    cart = session.get("cart", [])
    cart = [item for item in cart if item['id'] != item_id]
    session['cart'] = cart
    return redirect(url_for('main.cart'))

#管理者路由，檢查session中的is_admin確認是否為管理者，從資料庫中取得商品資料，並進入管理者頁面，導入商品資料
@main.route("/admin")
def admin():
    if not session.get("is_admin"):
        return redirect(url_for('main.error', msg="您沒有權限存取此頁面"))

    products = Product.query.all()
    return render_template("admin.html", products=products)

#管理員新增商品頁面，檢查新增商品欄位是否填寫完整，完整則將產品加入至資料庫中
@main.route("/add-product", methods=["POST"])
def add_product():
    if not session.get("is_admin"):
        return redirect(url_for('main.error', msg="權限不足"))
        
    name = request.form.get("name")
    price = request.form.get("price")
    description = request.form.get("description")
    image_url = request.form.get("image_url")
    
    if not all([name, price, description]):
         return redirect(url_for('main.error', msg="商品名稱、價格和描述為必填項"))

    new_product = Product(name=name, price=price, description=description, image_url=image_url, quantity=100)
    db.session.add(new_product)
    db.session.commit()
    return redirect(url_for('main.admin'))

@main.route("/delete-product/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    if not session.get("is_admin"):
        return redirect(url_for('main.error', msg="權限不足"))
        
    product = db.session.get(Product, product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
    return redirect(url_for('main.admin'))

@main.route('/checkout')
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    user = db.session.get(User, session['user_id'])
    
    # --- 加入 print 陳述句來檢查 ---
    print("\n--- 進入 checkout 路由 ---")
    print(f"找到的使用者: {user.nickname} (ID: {user.id})")
    
    cart_items = user.cart_items # 獲取購物車項目
    
    print(f"透過 user.cart_items 查詢到的購物車內容: {cart_items}")
    print(f"購物車項目數量: {len(cart_items) if cart_items else 0}")
    print("------------------------\n")
    # -----------------------------
    
    if not cart_items:
        return redirect(url_for('main.cart'))
    
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('checkout.html', cart_items = cart_items, total_price = total_price)

@main.route('/place_order', methods = ['POST'])
def place_order():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    user = db.session.get(User, session['user_id'])
    cart_items = user.cart_items
    
    if not cart_items:
        return redirect(url_for('main.error', msg = "您的購物車是空的"))
    
    shipping_address = request.form.get('shipping_address')
    if not shipping_address:
        return redirect(url_for('main.error', msg = "請填寫配送地址"))
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    
    new_order = Order(
        user_id = user.id,
        shipping_address = shipping_address,
        total_amount = total_amount
    )
    db.session.add(new_order)
    for item in cart_items:
        order_item = OrderItem(
            order = new_order,
            product_id = item.product.id,
            quantity = item.quantity,
            price = item.product.price
        )
        db.session.add(order_item)
    for item in cart_items:
        db.session.delete(item)
    db.session.commit()
    return render_template('order_success.html', order_id = new_order.id)    
    
        
