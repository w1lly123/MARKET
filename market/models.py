from . import db

#User模型
class User(db.Model):
    __tablename__="user"
    id = db.Column(db.Integer , primary_key=True)
    email =  db.Column(db.String(100), unique=True , nullable=False)
    nickname = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(255),nullable = False)
    is_admin = db.Column(db.Boolean,default = False, nullable = False)
#Product模型    
class Product(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100),nullable = False)
    price = db.Column(db.Numeric(10,2),nullable=False)
    quantity = db.Column(db.Integer,nullable = False)
    image_url = db.Column(db.String(200),nullable = False)
    description =  db.Column(db.Text,nullable = False)

class Order(db.Model):
    __tablename__ = "order"
    id = db.Column(db.Integer,primary_key = True)
    user_id = db.Column(db.Integer,db.ForeignKey("user.id"),nullable = False)
    product_id = db.Column(db.Integer,db.ForeignKey("product.id"),nullable = False)
    quantity = db.Column(db.Integer,nullable = False)
    order_date = db.Column(db.DateTime,nullable = False)
    price = db.Column(db.Numeric(10,2),nullable = False)
    status = db.Column(db.String(20),nullable = False)
    shipping_address = db.Column(db.String(200),nullable = False)
    