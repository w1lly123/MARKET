from flask import *
from flask_sqlalchemy import SQLAlchemy
import config
from models import db, User, Product


app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)

#首頁路由
@app.route("/")
def home():
    products = Product.query.all()
    return render_template("home.html",products = products)
@app.route("/error")
def error():
    msg = request.args.get("msg","發生錯誤，請重新連線")
    return render_template("error.html", msg = msg)
    
#註冊頁路由
@app.route("/register",methods = ["GET","POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    nickname = request.form.get("nickname")
    email = request.form.get("email")
    password = request.form.get("password")
    
    if not nickname or not email or not password:
        return redirect("/error?msg=所有欄位皆為必填")
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return redirect("/error?msg=該信箱已被註冊")
    new_user = User(nickname=nickname,email=email,password=password)
    db.session.add(new_user)
    db.session.commit()
    
    session["user_id"] = new_user.id
    session["nickname"] = new_user.nickname
    session["is_admin"] = new_user.is_admin
    
    return redirect("/")

#登入頁路由
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    email = request.form.get("email")
    password =  request.form.get("password")
    
    if not email or not password:
        return redirect("/error?msg=信箱或密碼輸入錯誤")
    
    user = User.query.filter_by(email = email,password = password).first()
    if not user:
        return  redirect("/error?msg=找不到該用戶")
    session["user_id"] = user.id
    session["nickname"] = user.nickname
    if user.is_admin:
        return redirect("/admin")
    else:
        return  redirect("/")    

#登出頁路由
@app.route("/logout")
def logout():
    session.pop("nickname","")
    session.pop("user_id","")
    session.pop("cart","")
    return redirect("/")

#執行資料庫建表(只需一次)
#with app.app_context():
    #User.__table__.create(db.engine)

#商品頁路由
@app.route("/product")
def product():
    products = Product.query.all()
    return render_template("product.html",products = products)

#購物車
@app.route("/cart")
def cart():
    if "user_id" not in session:
        return redirect("/login")
    cart_item = session.get("cart",[])
    
    total = sum(item["price"] * item["quantity"] for item in cart_item)
    
    return render_template("cart.html",cart_item = cart_item, total = total)

#加入購物車
@app.route("/add-to-cart/<product_id>",methods=["GET"])
def add(product_id):
    if "user_id" not in  session:
        return redirect("/login")
    product = Product.query.get(product_id)
    if not product:
        return redirect("/error?msg=找不到此商品") 
    cart = session.get("cart",[])
    
    for item in cart:
        if item["id"] == product.id:
            item["quantity"] += 1
            break
    else:
        cart.append({
            "id": product.id,
            "price": float(product.price),
            "quantity": 1
        })
    session["cart"] = cart
    return redirect("/cart")

@app.route("/admin")
def admin():
    if "user_id" not in session:
        return redirect("/login")
    current_user = User.query.get(session["user_id"])
    if not current_user or not current_user.is_admin:
        return redirect("/error?msg=您沒有權限存取此頁面")

    products = Product.query.all()
    return render_template("admin.html",products = products)
       

@app.route("/add-product",methods = ["POST"])
def add_product():
    price = request.form.get("price")
    quantity = request.form.get("quantity")
    description = request.form.get("description")
    image_url = request.form.get("image_url")
    
    new_product = Product(price = price, quantity = quantity, image_url = image_url,description = description)
    db.session.add(new_product)
    db.session.commit()
    return redirect("/admin")

@app.route("/delete-product/<product_id>",methods=["POST"])
def del_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return redirect("/error?msg=找不到此商品")
    db.session.delete(product)
    db.session.commit()
    return redirect("/admin")
if __name__ == "__main__":
    app.run(debug=True, port = 3000)