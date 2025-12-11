import bcrypt
from flask import Flask, request, jsonify
from models.user import User
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin123@127.0.0.1:3306/diet-control'
db.init_app(app)

# criar rota para cadastro de novo usuário
@app.route("/user", methods=["POST"])
def create_user():
    data = request.json # pegar os dados do corpo da requisição
    username = data.get("username")
    password = data.get("password") 

    if username and password:
        return jsonify({"message": "User created", "username": username}), 201
    else:
        return jsonify({"message": "Invalid data"}), 400

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created", "username": username}), 201

return jsonify({"message": "Invalid data"}), 400


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    return jsonify({"message": "Login route hit", "username": username}), 200

if __name__ == "__main__":
    app.run(debug=True)
    