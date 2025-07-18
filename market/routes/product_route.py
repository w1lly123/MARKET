from flask import Blueprint
from market.controllers import product_controller

product_bp = Blueprint('product', __name__)

@product_bp.route("/")
def home():
    return product_controller.home()

@product_bp.route("/product/<int:product_id>")
def product_detail(product_id):
    return product_controller.product(product_id)

@product_bp.route("/admin")
def admin():
    return product_controller.admin()

@product_bp.route("/add-product", methods=["POST"])
def add_product():
    return product_controller.add_product()

@product_bp.route("/delete-product/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    return product_controller.delete_product(product_id)

@product_bp.route("/admin/orders")
def admin_orders():
    return product_controller.admin_orders()
@product_bp.route("/error")
def error():
    return product_controller.error()
