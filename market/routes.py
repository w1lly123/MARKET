# 檔案: market/routes.py (最終正確版本)

from flask import render_template, request, redirect, url_for, Blueprint, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
# 【修正】匯入所有需要的模型
from .models import User, Product, CartItem, Order, OrderItem
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity, get_jwt,
    set_access_cookies, unset_jwt_cookies, get_csrf_token
)

main = Blueprint('main', __name__)

# --- 公開路由 ---
@main.route("/")
def home():
    products = Product.query.all()
    return render_template("home.html", products=products)

@main.route("/error")
def error():
    msg = request.args.get("msg", "發生錯誤，請重新連線")
    return render_template("error.html", msg=msg)

# --- 驗證路由 ---
@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    # ... (您的註冊邏輯是正確的) ...
    nickname, email, password = request.form.get("nickname"), request.form.get("email"), request.form.get("password")
    if not all([nickname, email, password]):
        return redirect(url_for('main.error', msg="所有欄位皆為必填"))
    if User.query.filter_by(email=email).first():
        return redirect(url_for('main.error', msg="該信箱已被註冊"))
    
    new_user = User(nickname=nickname, email=email, password=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()
    
    identity = new_user.id
    additional_claims = {"nickname": new_user.nickname, "is_admin": new_user.is_admin}
    access_token = create_access_token(identity=identity, additional_claims=additional_claims)
    
    response = make_response(redirect(url_for('main.home')))
    set_access_cookies(response, access_token)
    return response

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    # ... (您的登入邏輯是正確的) ...
    email, password = request.form.get("email"), request.form.get("password")
    if not email or not password:
        return redirect(url_for('main.error', msg="信箱或密碼輸入錯誤"))
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return redirect(url_for('main.error', msg="帳號或密碼錯誤"))
        
    identity = user.id
    additional_claims = {"nickname": user.nickname, "is_admin": user.is_admin}
    access_token = create_access_token(identity=identity, additional_claims=additional_claims)

    redirect_url = url_for('main.admin') if user.is_admin else url_for('main.home')
    response = make_response(redirect(redirect_url))
    set_access_cookies(response, access_token)
    return response

@main.route("/logout")
@jwt_required()
def logout():
    response = make_response(redirect(url_for('main.home')))
    unset_jwt_cookies(response)
    return response

# --- 內容頁與表單頁 ---
@main.route("/product/<int:product_id>")
@jwt_required(optional=True)
def product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return redirect(url_for('main.error', msg="找不到此商品"))
    
    csrf_token = None
    encoded_token = request.cookies.get('access_token_cookie')
    if encoded_token:
        csrf_token = get_csrf_token(encoded_token)
        
    # 【修正】將 csrf_token 傳遞給模板
    return render_template("product.html", product=product, csrf_token=csrf_token)

@main.route("/cart")
@jwt_required()
def cart():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    cart_items = user.cart_items
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    csrf_token = None
    encoded_token = request.cookies.get('access_token_cookie')
    if encoded_token:
        csrf_token = get_csrf_token(encoded_token)
    
    # 【修正】將 csrf_token 傳遞給模板
    return render_template("cart.html", cart_items=cart_items, total_price=total_price, csrf_token=csrf_token)

@main.route("/admin")
@jwt_required()
def admin():
    if not get_jwt().get("is_admin"):
        return redirect(url_for('main.error', msg="您沒有權限存取此頁面"))
        
    products = Product.query.all()
    
    csrf_token = None
    encoded_token = request.cookies.get('access_token_cookie')
    if encoded_token:
        csrf_token = get_csrf_token(encoded_token)
        
    # 【修正】將 csrf_token 傳遞給模板
    return render_template("admin.html", products=products, csrf_token=csrf_token)

@main.route('/checkout')
@jwt_required()
def checkout():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    cart_items = user.cart_items
    if not cart_items:
        return redirect(url_for('main.cart'))
        
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    csrf_token = None
    encoded_token = request.cookies.get('access_token_cookie')
    if encoded_token:
        csrf_token = get_csrf_token(encoded_token)

    # 【修正】將 csrf_token 傳遞給模板
    return render_template('checkout.html', cart_items=cart_items, total_price=total_price, csrf_token=csrf_token)

# --- POST 動作路由 ---
@main.route("/add-to-cart", methods=["POST"])
@jwt_required()
def add_to_cart():
    user_id, product_id = get_jwt_identity(), request.form.get("product_id")
    quantity = int(request.form.get("quantity", 1))
    
    if not db.session.get(Product, product_id):
        return redirect(url_for('main.error', msg="找不到此商品"))
    
    cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        db.session.add(CartItem(user_id=user_id, product_id=product_id, quantity=quantity))
    
    db.session.commit()
    return redirect(url_for('main.cart'))

@main.route("/remove-from-cart/<int:item_id>", methods=['POST'])
@jwt_required()
def remove_from_cart(item_id):
    user_id = get_jwt_identity()
    cart_item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
    return redirect(url_for('main.cart'))

@main.route("/add-product", methods=["POST"])
@jwt_required()
def add_product():
    if not get_jwt().get("is_admin"):
        return redirect(url_for('main.error', msg="權限不足"))
    # ... (您的新增商品邏輯是正確的) ...
    form_data = request.form
    if not all([form_data.get("name"), form_data.get("price"), form_data.get("description")]):
        return redirect(url_for('main.error', msg="商品名稱、價格和描述為必填項"))
    new_product = Product(name=form_data.get("name"), price=form_data.get("price"), description=form_data.get("description"), image_url=form_data.get("image_url"), quantity=100)
    db.session.add(new_product)
    db.session.commit()
    return redirect(url_for('main.admin'))

@main.route("/delete-product/<int:product_id>", methods=["POST"])
@jwt_required()
def delete_product(product_id):
    if not get_jwt().get("is_admin"):
        return redirect(url_for('main.error', msg="權限不足"))
    product = db.session.get(Product, product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
    return redirect(url_for('main.admin'))

@main.route('/place_order', methods=['POST'])
@jwt_required()
def place_order():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    cart_items = user.cart_items
    
    if not cart_items:
        return redirect(url_for('main.error', msg="您的購物車是空的"))
    shipping_address = request.form.get('shipping_address')
    if not shipping_address:
        return redirect(url_for('main.error', msg="請填寫配送地址"))
    
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    new_order = Order(user_id=user.id, shipping_address=shipping_address, total_amount=total_amount)
    db.session.add(new_order)
    
    # 【修正】修正了迴圈邏輯
    for item in cart_items:
        db.session.add(OrderItem(order=new_order, product_id=item.product.id, quantity=item.quantity, price=item.product.price))
    
    for item in cart_items:
        db.session.delete(item)
    
    db.session.commit()
    return render_template('order_success.html', order_id=new_order.id)
