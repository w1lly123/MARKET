from flask import request, render_template, redirect, url_for, make_response
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies, jwt_required
from market.models import User
from market import db

def register():
    if request.method == 'POST':
        data = request.form
        if User.query.filter_by(email=data.get('email')).first():
            return redirect(url_for('product.error', msg="該信箱已被註冊"))
        
        new_user = User(nickname=data.get('nickname'), email=data.get('email'))
        new_user.set_password(data.get('password'))
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('auth.login'))
    return render_template("auth/register.html")

def login():
    if request.method == 'POST':
        data = request.form
        user = User.query.filter_by(email=data.get('email')).first()
        
        if not user or not user.check_password(data.get('password')):
            return redirect(url_for('product.error', msg="帳號或密碼錯誤"))
        
        identity = user.id
        additional_claims = {"nickname": user.nickname, "is_admin": user.is_admin}
        access_token = create_access_token(identity=identity, additional_claims=additional_claims)
        
        redirect_url = url_for('product.admin') if user.is_admin else url_for('product.home')
        response = make_response(redirect(redirect_url))
        set_access_cookies(response, access_token)
        return response
    return render_template("auth/login.html")

@jwt_required()
def logout():
    response = make_response(redirect(url_for('product.home')))
    unset_jwt_cookies(response)
    return response
