from market import create_app, db
from market.models import User
import click

app = create_app()
if __name__ == "__main__":
    app.run(debug=True, port = 3000)

##flask promote-admin your_admin_email@example.com    
@app.cli.command("promote-admin")
@click.argument("email")
def promote_admin(email):
    user  = User.query.filter_by(email =  email).first()
    if not user:
        print(f"錯誤:找不到email為{email}的使用者")
        return
    user.is_admin = True
    db.session.commit()
    print(f"已將{user.nickname}({email})設為管理者")