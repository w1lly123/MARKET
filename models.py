from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#User模型
class User(db.Model):
    __tablename__="user"
    id = db.Column(db.Integer , primary_key=True)
    email =  db.Column(db.String(100), unique=True , nullable=False)
    nickname = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(128),nullable = False)
    is_admin = db.Column(db.Boolean,default = False, nullable = False)
#Product模型    
class Product(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key = True)
    price = db.Column(db.Numeric(10,2),nullable=False)
    quantity = db.Column(db.Integer,nullable = False)
    image_url = db.Column(db.String(200),nullable = False)
    description =  db.Column(db.Text,nullable = False)
    