from . import db
from datetime import datetime

#User模型
class User(db.Model):
    __tablename__="user"
    id = db.Column(db.Integer , primary_key=True)
    email =  db.Column(db.String(100), unique=True , nullable=False)
    nickname = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(255),nullable = False)
    is_admin = db.Column(db.Boolean,default = False, nullable = False)
    cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade="all, delete-orphan")
#Product模型    
class Product(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100),nullable = False)
    price = db.Column(db.Numeric(10,2),nullable=False)
    quantity = db.Column(db.Integer,nullable = False)
    image_url = db.Column(db.String(200),nullable = False)
    description =  db.Column(db.Text,nullable = False)

class CartItem(db.Model):
    __tablename__ = 'cart_item'
    id = db.Column(db.Integer,primary_key = True, default = 1)
    
    #與User和Product建立多對一外件關聯
    user_id = db.Column(db.Integer , db.ForeignKey('user.id'), nullable = False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"),nullable = False)
    
    product = db.relationship('Product')

class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    shipping_address = db.Column(db.String(255), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending') # e.g., Pending, Shipped, Delivered

    # 建立 Order 和 OrderItem 之間的一對多關聯
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")
    
class OrderItem(db.Model):
    __tablename__ = 'order_item'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False) # 儲存下單當時的價格

    product = db.relationship('Product')