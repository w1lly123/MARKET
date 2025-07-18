from flask import render_template, request, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt
from market.models import Product, Order, User
from market import db

def home():
    products = Product.query.all()
    return render_template("product/home.html", products=products)

def product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return redirect(url_for('product.error', msg="找不到此商品"))
    return render_template("product/product.html", product=product)

@jwt_required()
def admin():
    if not get_jwt().get("is_admin"):
        return redirect(url_for('product.error', msg="您沒有權限存取此頁面"))
    products = Product.query.all()
    return render_template("product/admin.html", products=products)

@jwt_required()
def add_product():
    if not get_jwt().get("is_admin"):
        return redirect(url_for('product.error', msg="權限不足"))
    form_data = request.form
    new_product = Product(
        name=form_data.get("name"), 
        price=int(form_data.get("price")), 
        description=form_data.get("description"), 
        image_url=form_data.get("image_url")
    )
    db.session.add(new_product)
    db.session.commit()
    return redirect(url_for('product.admin'))

@jwt_required()
def delete_product(product_id):
    if not get_jwt().get("is_admin"):
        return redirect(url_for('product.error', msg="權限不足"))
    product = db.session.get(Product, product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
    return redirect(url_for('product.admin'))

@jwt_required()
def admin_orders():
    if not get_jwt().get("is_admin"):
        return redirect(url_for('product.error', msg = "您沒有權限存取此頁面"))
    search_order_id  = request.args.get('order_id','').strip()
    search_user_email = request.args.get('user_email','').strip()
    
    query = Order.query.order_by(Order.created_at.desc())
    if search_order_id:
        query = query.filter(Order.id.ilike(f"${search_order_id}$"))
    if search_user_email:
        query = query.join(User).filter(User.email.ilike(f"%{search_user_email}%"))
    
    orders = query.all()
    return render_template(
        "product/admin_orders.html",
        orders = orders,
        search_order_id = search_order_id,
        search_user_email = search_user_email
    )
    

def error():
    msg = request.args.get("msg", "發生錯誤，請重新連線")
    return render_template("product/error.html", msg=msg)