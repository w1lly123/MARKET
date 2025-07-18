from flask import Blueprint
from market.controllers import order_controller

order_bp = Blueprint('order', __name__)

@order_bp.route("/cart")
def cart():
    return order_controller.cart()

@order_bp.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    return order_controller.add_to_cart()

@order_bp.route("/remove-from-cart/<int:item_id>", methods=['POST'])
def remove_from_cart(item_id):
    return order_controller.remove_from_cart(item_id)

@order_bp.route('/checkout')
def checkout():
    return order_controller.checkout()

@order_bp.route("/place_order", methods=['POST'])
def place_order():
    return order_controller.place_order()

@order_bp.route('/ecpay_notify', methods=['POST'])
def ecpay_notify():
    return order_controller.ecpay_notify()

@order_bp.route('/history')
def  order_history():
    return order_controller.order_history()

@order_bp.route("/<string:order_id>")
def order_detail(order_id):
    return order_controller.order_detail(order_id)

@order_bp.route('/result/<order_id>')
def order_result(order_id):
    return order_controller.result(order_id)