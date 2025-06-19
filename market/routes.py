# 修正點：精確導入，而不是用 *
from flask import render_template, request, redirect, url_for, session, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User, Product

main = Blueprint('main', __name__)

@main.route("/")
def home():
    products = Product.query.all()
    return render_template("home.html", products=products)

@main.route("/error")
def error():
    msg = request.args.get("msg", "發生錯誤，請重新連線")
    return render_template("error.html", msg=msg)

@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    
    nickname = request.form.get("nickname")
    email = request.form.get("email")
    password = request.form.get("password")
    
    if not nickname or not email or not password:
        # 修正點：使用 url_for
        return redirect(url_for('main.error', msg="所有欄位皆為必填"))
        
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        # 修正點：使用 url_for
        return redirect(url_for('main.error', msg="該信箱已被註冊"))

    # 【安全性修正】密碼加密
    hashed_password = generate_password_hash(password)
    new_user = User(nickname=nickname, email=email, password=hashed_password)
    
    db.session.add(new_user)
    db.session.commit()
    
    session["user_id"] = new_user.id
    session["nickname"] = new_user.nickname
    session["is_admin"] = new_user.is_admin
    
    # 修正點：使用 url_for
    return redirect(url_for('main.home'))

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    email = request.form.get("email")
    password = request.form.get("password")
    
    if not email or not password:
        return redirect(url_for('main.error', msg="信箱或密碼輸入錯誤"))
    
    user = User.query.filter_by(email=email).first()

    # 【安全性修正】比對加密後的密碼，並使用模糊錯誤訊息
    if not user or not check_password_hash(user.password, password):
        return redirect(url_for('main.login', msg="帳號或密碼錯誤"))
        
    session["user_id"] = user.id
    session["nickname"] = user.nickname
    session["is_admin"] = user.is_admin

    if user.is_admin:
        # 修正點：使用 url_for
        return redirect(url_for('main.admin'))
    else:
        # 修正點：使用 url_for
        return redirect(url_for('main.home'))

@main.route("/logout")
def logout():
    # 修正點：使用 session.clear() 更簡潔
    session.clear()
    return redirect(url_for('main.home'))

@main.route("/product/<int:product_id>")
def product(product_id):
    # 修正點：使用 db.session.get()
    product = db.session.get(Product, product_id)
    if not product:
        return redirect(url_for('main.error', msg="找不到此商品"))
    return render_template("product.html", product=product)

@main.route("/cart")
def cart():
    if "user_id" not in session:
        return redirect(url_for('main.login'))
    
    cart_items = session.get("cart", [])
    # 修正點：將變數命名為 cart_items 以匹配模板
    total_price = sum(float(item["price"]) * item["quantity"] for item in cart_items)
    
    return render_template("cart.html", cart_items=cart_items, total_price=total_price)

@main.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    if "user_id" not in session:
        return redirect(url_for('main.login'))

    product_id = request.form.get("product_id")
    quantity = int(request.form.get("quantity", 1))

    if not product_id:
        return redirect(url_for('main.error', msg="未提供商品 ID"))

    product = db.session.get(Product, product_id)
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

@main.route("/remove-from-cart/<int:item_id>")
def remove_from_cart(item_id):
    cart = session.get("cart", [])
    cart = [item for item in cart if item['id'] != item_id]
    session['cart'] = cart
    return redirect(url_for('main.cart'))

@main.route("/admin")
def admin():
    if not session.get("is_admin"):
        return redirect(url_for('main.error', msg="您沒有權限存取此頁面"))

    products = Product.query.all()
    return render_template("admin.html", products=products)

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