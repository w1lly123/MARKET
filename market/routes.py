# 檔案: market/routes.py (重構後的版本)

from flask import request, Blueprint
from flask_jwt_extended import jwt_required
from . import controllers

main = Blueprint('main', __name__)

# --- 公開頁面路由 ---
@main.route("/")
def home():
    return controllers.show_home_page()

@main.route("/error")
def error():
    return controllers.show_error_page()

@main.route("/product/<int:product_id>")
@jwt_required(optional=True)
def product(product_id):
    return controllers.show_product_page(product_id)

# --- 驗證流程路由 ---
@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        return controllers.handle_register_form()
    return controllers.show_register_page()

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        return controllers.handle_login_form()
    return controllers.show_login_page()

@main.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    return controllers.handle_logout()

# --- 使用者功能路由 ---
@main.route("/cart")
@jwt_required()
def cart():
    return controllers.show_cart_page()

@main.route("/add-to-cart", methods=["POST"])
@jwt_required()
def add_to_cart():
    return controllers.handle_add_to_cart()

@main.route("/remove-from-cart/<int:item_id>", methods=['POST'])
@jwt_required()
def remove_from_cart(item_id):
    return controllers.handle_remove_from_cart(item_id)

@main.route('/checkout')
@jwt_required()
def checkout():
    return controllers.show_checkout_page()

@main.route('/place_order', methods=['POST'])
@jwt_required()
def place_order():
    return controllers.handle_place_order()

# --- 管理員路由 ---
@main.route("/admin")
@jwt_required()
def admin():
    return controllers.show_admin_page()

@main.route("/add-product", methods=["POST"])
@jwt_required()
def add_product():
    return controllers.handle_add_product()

@main.route("/delete-product/<int:product_id>", methods=["POST"])
@jwt_required()
def delete_product(product_id):
    return controllers.handle_delete_product(product_id)