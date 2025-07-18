import uuid
from flask import request, current_app, redirect, url_for, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from market.models import User, Order, OrderItem, CartItem
from market import db
from datetime import datetime
import random

try:
    from market.ecpay_payment_sdk import ECPayPaymentSdk
except ImportError:
    class ECPayPaymentSdk:
        def __init__(self, **kwargs): pass
        def create_order(self, **kwargs): return {}
        def generate_check_value(self, **kwargs): return ""

@jwt_required()
def cart():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    total_price = sum(item.product.price * item.quantity for item in user.cart_items)
    return render_template("order/cart.html", cart_items=user.cart_items, total_price=total_price)

@jwt_required()
def add_to_cart():
    user_id = get_jwt_identity()
    product_id = request.form.get("product_id")
    quantity = int(request.form.get("quantity", 1))
    cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        db.session.add(CartItem(user_id=user_id, product_id=product_id, quantity=quantity))
    db.session.commit()
    return redirect(url_for('order.cart'))

@jwt_required()
def remove_from_cart(item_id):
    user_id = get_jwt_identity()
    cart_item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
    return redirect(url_for('order.cart'))

@jwt_required()
def checkout():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user.cart_items:
        return redirect(url_for('order.cart'))
    total_price = sum(item.product.price * item.quantity for item in user.cart_items)
    return render_template('order/checkout.html', cart_items=user.cart_items, total_price=total_price)

@jwt_required()
def place_order():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user.cart_items:
        return redirect(url_for('order.cart'))
    try:
        total_amount = sum(item.product.price * item.quantity for item in user.cart_items)
        
        merchant_trade_no = str(uuid.uuid4()).replace('-', '')[:20]

        new_order = Order(
            id=merchant_trade_no, user_id=user.id, total_amount=total_amount,
            shipping_address=request.form.get('shipping_address'), status="pending"
        )
        db.session.add(new_order)
        for item in user.cart_items:
            db.session.add(OrderItem(order_id=new_order.id, product_id=item.product.id, quantity=item.quantity, price=item.product.price))
        db.session.commit()

        # 【關鍵修正】替換成您的 ngrok 公開網址
        notify_url = 'https://26b4f8694156.ngrok-free.app/order/ecpay_notify'
        
        print("--- 準備發送到綠界的 URL ---")
        print(f"後端通知 (ReturnURL): {notify_url}")
        print("--------------------------")

        ecpay_payment_sdk = ECPayPaymentSdk(
            MerchantID=current_app.config['ECPAY_MERCHANT_ID'],
            HashKey=current_app.config['ECPAY_HASH_KEY'],
            HashIV=current_app.config['ECPAY_HASH_IV']
        )
        order_params = {
            'MerchantTradeNo': merchant_trade_no,
            'MerchantTradeDate': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
            'PaymentType': 'aio',
            'TotalAmount': int(total_amount),
            'TradeDesc': '我的商店 - 訂單',
            'ItemName': '商品一批',
            'ReturnURL': notify_url,  # 使用 ngrok 的公開網址
            'ClientBackURL': url_for('order.order_result', order_id=merchant_trade_no, _external=True),
            'ChoosePayment': 'ALL',
        }
        final_order_params = ecpay_payment_sdk.create_order(order_params)
        payment_info = {
            'action': current_app.config['ECPAY_API_URL'],
            'parameters': final_order_params
        }
        return render_template('order/ecpay_checkout.html', payment_info=payment_info)
    except Exception as e:
        db.session.rollback()
        return redirect(url_for('product.error', msg=f"訂單處理失敗: {str(e)}"))

def ecpay_notify():
    merchant_trade_no = None
    try:
        post_data = request.form.to_dict()
        merchant_trade_no = post_data.get('MerchantTradeNo')

        ecpay_payment_sdk = ECPayPaymentSdk(
            MerchantID=current_app.config['ECPAY_MERCHANT_ID'],
            HashKey=current_app.config['ECPAY_HASH_KEY'],
            HashIV=current_app.config['ECPAY_HASH_IV']
        )
        received_mac = post_data.pop('CheckMacValue', '')
        expected_mac = ecpay_payment_sdk.generate_check_value(post_data)

        if received_mac != expected_mac:
            print(f"訂單 {merchant_trade_no} 簽章驗證失敗！")
            return "Error"
            
        rtn_code = post_data.get('RtnCode')
        if rtn_code == '1':
            order = db.session.get(Order, merchant_trade_no)
            if order and order.status == 'pending':
                order.status = 'paid'
                CartItem.query.filter_by(user_id=order.user_id).delete()
                db.session.commit()
    except Exception as e:
        print(f"處理訂單 {merchant_trade_no} 的後端通知時發生錯誤: {e}")
        return "Error"
    return '1|OK'

@jwt_required()
def result(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return redirect(url_for('product.error', msg="找不到此訂單"))
    if order.status == 'paid':
        return render_template('order/order_success.html', order_id=order.id)
    else:
        return redirect(url_for('product.error', msg=f"訂單 {order.id} 付款失敗或仍在處理中。"))
    
@jwt_required()
def order_history():
    user_id = get_jwt_identity()
    orders = Order.query.filter_by(user_id = user_id).order_by(Order.created_at.desc()).all()
    return render_template('order/order_history.html', orders = orders)

@jwt_required()
def order_detail(order_id):
    user_id = get_jwt_identity()
    order = Order.query.filter_by(id = order_id, user_id = user_id).first()
    if  not order:
        return redirect(url_for('product.error', msg=f"訂單 {order.id} 找不到該訂單詳細資訊。"))
    return render_template('order/order_detail.html', order = order)