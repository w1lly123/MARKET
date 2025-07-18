from market import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'order'
    #使用字串作為PK，以儲存金流商提供的唯一訂單編號
    id = db.Column(db.String(50), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    total_amount = db.Column(db.Integer, nullable=False)
    
    shipping_address = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")