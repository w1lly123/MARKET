# 檔案: market/controllers.py (新檔案)

from flask import render_template, request, redirect, url_for, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User, Product, CartItem, Order, OrderItem
from flask_jwt_extended import (
    create_access_token, get_jwt_identity, get_jwt,
    set_access_cookies, unset_jwt_cookies, get_csrf_token
)

# --- 渲染頁面 (Page Rendering) 的 Controllers ---

def show_home_page():
    """顯示首頁"""
    products = Product.query.all()
    return render_template("home.html", products=products)

def show_error_page():
    """顯示錯誤頁面"""
    msg = request.args.get("msg", "發生錯誤，請重新連線")
    return render_template("error.html", msg=msg)

def show_register_page():
    """顯示註冊頁面"""
    return render_template("register.html")

def show_login_page():
    """顯示登入頁面"""
    return render_template("login.html")

def show_product_page(product_id):
    """顯示單一商品詳情頁"""
    product = db.session.get(Product, product_id)
    if not product:
        return redirect(url_for('main.error', msg="找不到此商品"))
    
    csrf_token = None
    encoded_token = request.cookies.get('access_token_cookie')
    if encoded_token:
        csrf_token = get_csrf_token(encoded_token)
        
    return render_template("product.html", product=product, csrf_token=csrf_token)

def show_cart_page():
    """顯示購物車頁面"""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    cart_items = user.cart_items
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    csrf_token = None
    encoded_token = request.cookies.get('access_token_cookie')
    if encoded_token:
        csrf_token = get_csrf_token(encoded_token)
        
    return render_template("cart.html", cart_items=cart_items, total_price=total_price, csrf_token=csrf_token)

def show_admin_page():
    """顯示管理後台頁面"""
    if not get_jwt().get("is_admin"):
        return redirect(url_for('main.error', msg="您沒有權限存取此頁面"))
        
    products = Product.query.all()
    
    csrf_token = None
    encoded_token = request.cookies.get('access_token_cookie')
    if encoded_token:
        csrf_token = get_csrf_token(encoded_token)
        
    return render_template("admin.html", products=products, csrf_token=csrf_token)

def show_checkout_page():
    """顯示結帳頁面"""
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

    return render_template('checkout.html', cart_items=cart_items, total_price=total_price, csrf_token=csrf_token)

# --- 處理動作 (Action Handling) 的 Controllers ---

def handle_register_form():
    """處理註冊表單提交"""
    nickname = request.form.get("nickname")
    email = request.form.get("email")
    password = request.form.get("password")
    
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

def handle_login_form():
    """處理登入表單提交"""
    email = request.form.get("email")
    password = request.form.get("password")
    
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

def handle_logout():
    """處理登出"""
    response = make_response(redirect(url_for('main.home')))
    unset_jwt_cookies(response)
    return response

def handle_add_to_cart():
    """處理加入購物車"""
    user_id = get_jwt_identity()
    product_id = request.form.get("product_id")
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

def handle_remove_from_cart(item_id):
    """處理從購物車移除商品"""
    user_id = get_jwt_identity()
    cart_item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
    return redirect(url_for('main.cart'))

def handle_add_product():
    """處理新增商品"""
    if not get_jwt().get("is_admin"):
        return redirect(url_for('main.error', msg="權限不足"))
    
    form_data = request.form
    if not all([form_data.get("name"), form_data.get("price"), form_data.get("description")]):
        return redirect(url_for('main.error', msg="商品名稱、價格和描述為必填項"))
    
    new_product = Product(
        name=form_data.get("name"), 
        price=form_data.get("price"), 
        description=form_data.get("description"), 
        image_url=form_data.get("image_url"), 
        quantity=100
    )
    db.session.add(new_product)
    db.session.commit()
    return redirect(url_for('main.admin'))

def handle_delete_product(product_id):
    """處理刪除商品"""
    if not get_jwt().get("is_admin"):
        return redirect(url_for('main.error', msg="權限不足"))
        
    product = db.session.get(Product, product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
    return redirect(url_for('main.admin'))

def handle_place_order():
    """處理下訂單"""
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
    
    for item in cart_items:
        db.session.add(OrderItem(order=new_order, product_id=item.product.id, quantity=item.quantity, price=item.product.price))
    
    for item in cart_items:
        db.session.delete(item)
    
    db.session.commit()
    return render_template('order_success.html', order_id=new_order.id)