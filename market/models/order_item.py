from market import db

class OrderItem(db.Model):
    __tablename__ = 'order_item'
    id = db.Column(db.Integer, primary_key=True)
    
    order_id = db.Column(db.String(50), db.ForeignKey('order.id'), nullable=False)
    
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    
    price = db.Column(db.Integer, nullable=False)

    product = db.relationship('Product')