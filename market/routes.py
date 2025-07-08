from flask import request, Blueprint
from flask_jwt_extended import jwt_required
from . import controllers

main = Blueprint('main', __name__)

@main.route("/")
def home():
    return controllers.home()

@main.route("/error")
def error():
    return controllers.error()

@main.route("/product/<int:product_id>")
@jwt_required(optional=True)
def product(product_id):
    return controllers.product(product_id)

@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        return controllers.register()
    return controllers.register()

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        return controllers.login()
    return controllers.login()

@main.route("/cart")
@jwt_required()
def cart():
    return controllers.cart()

@main.route("/add-to-cart", methods=["POST"])
@jwt_required()
def add_to_cart():
    return controllers.add_to_cart()

@main.route("/remove-from-cart/<int:item_id>", methods=['POST'])
@jwt_required()
def remove_from_cart(item_id):
    return controllers.remove_from_cart(item_id)

@main.route('/checkout')
@jwt_required()
def checkout():
    return controllers.checkout()

@main.route('/place_order', methods=['POST'])
@jwt_required()
def place_order():
    return controllers.place_order()

@main.route("/admin")
@jwt_required()
def admin():
    return controllers.admin()

@main.route("/add-product", methods=["POST"])
@jwt_required()
def add_product():
    return controllers.add_product()

@main.route("/delete-product/<int:product_id>", methods=["POST"])
@jwt_required()
def delete_product(product_id):
    return controllers.delete_product(product_id)