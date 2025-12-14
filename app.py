import bcrypt
from flask import Flask, request, jsonify
from models.user import User
from models.meal import Meal
from datetime import datetime
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin123@127.0.0.1:3307/diet-control'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Inicializar LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ADICIONAR: Criar tabelas automaticamente
# with app.app_context():
#    db.create_all()

# recuperar usuário pelo ID, função obrigatória do flask-login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# rota para criar novo usuário
@app.route("/user", methods=["POST"])
def create_user():
    """Criar novo usuário"""
    data = request.json # pegar os dados do corpo da requisição
    username = data.get("username")
    password = data.get("password") 

    if not username or not password:
        return jsonify({"message": "Username e password são obrigatórios"}), 400

    # Verificar se os dados são válidos
    if username and password:
        if User.query.filter_by(username=username).first(): # Verificar se o usuário já existe
            return jsonify({"message": "Usuário já existe"}), 400
        
        # Criptografar a senha recebida para comparar com a do banco de dados       
        hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())

    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Usuário criado com sucesso", "username": username}), 201

    return jsonify({"message": "Dados inválidos"}), 400

# Rota para fazer Login no sistema
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username e password são obrigatórios"}), 400

    user = User.query.filter_by(username=username).first() # Buscar usuário no banco de dados

    # Verifica se o usuário existe e se a senha está correta usando bcrypt
    if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
        login_user(user)            
        print(f"Aqui Está o Resultado, {current_user.is_authenticated}")
        return jsonify({"message": "Credenciais estão ok, você está Logado no Sistema!!!"}), 200


    return jsonify({"message": "Credenciais Inválidas"}), 401

# Sair da aplicação, fazer o Logout
@app.route("/logout", methods=["GET"])
def logout():
    if not current_user.is_authenticated:
        return jsonify({"message": "Você já está deslogado do sistema"}), 400

    logout_user()
    return jsonify({"message": "Logout realizado com sucesso"}), 200

# ==== Rotas de Refeições (Meals) ====

# Criar nova refeição
@app.route("/meals", methods=["POST"])
@login_required
def create_meal():
    data = request.json

    name = data.get("name")
    description = data.get("description")
    datetime_str = data.get("datetime")
    is_on_diet = data.get("is_on_diet")

    if not name or not description or not datetime_str or is_on_diet is None:
        return jsonify({"message": "Todos os campos são obrigatórios"}), 400

    
    # Validar o formato da data (somente DD/MM/YYYY, sem hora)
    meal_datetime = None
    if datetime_str:
        date_formats = [
            '%d/%m/%Y',    # 13/12/2025
            '%d-%m-%Y',    # 13-12-2025
        ]
        
        parsed = False
        for fmt in date_formats:
            try:
                meal_datetime = datetime.strptime(datetime_str, fmt)
                parsed = True
                break
            except ValueError:
                continue
        
        if not parsed:
            return jsonify({
                "message": "Formato de data inválido",
                "formatos_aceitos": [
                    "DD/MM/YYYY (ex: 13/12/2025)",
                    "DD-MM-YYYY (ex: 13-12-2025)"
                ]
            }), 400
    else:
        return jsonify({"message": "A data é obrigatória"}), 400

    if 'is_on_diet' in data:
        is_on_diet = data['is_on_diet']
        # ✅ ADICIONAR: Converter string para boolean
        if isinstance(is_on_diet, str):
            is_on_diet = is_on_diet.lower() in ['true', '1', 'yes', 'sim']
        

    new_meal = Meal(
        name=name,
        description=description,
        datetime=meal_datetime,
        is_on_diet=is_on_diet,
        user_id=current_user.id
    )

    db.session.add(new_meal)
    db.session.commit()

    return jsonify({
        "message": "Refeição criada com sucesso",
        "meal": new_meal.to_dict()
    }), 201


if __name__ == "__main__":
    app.run(debug=True)
    