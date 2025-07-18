from market import db

class Product(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    price = db.Column(db.Integer, nullable=False)
    
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)