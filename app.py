from flask import Flask, request, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, fresh_login_required,current_user
from database import db
from models.user import User
from models.food import Food
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin123@127.0.0.1:3307/food-crud'

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)

login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username and password:

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
            login_user(user)
            print(current_user.is_authenticated)
            return jsonify({"message": "Login bem sucedido"})
    return jsonify({"message": "Credenciais inválidas"}), 400

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout bem-sucedido"})

@app.route('/user', methods=['POST'])
def create_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "Usuário criado com sucesso!"})
    
    return jsonify({"message": "Dados inválidos"}), 400

@app.route('/food', methods=['POST'])
def create_food():
    data = request.json
    name = data.get("name")
    description = data.get("description")
    date = data.get("date")
    included = data.get("included")
    user_id = current_user.id

    if name and description and date and included is not None:
        food = Food(name=name , description=description, date=date, included=included, user_id=user_id)
        db.session.add(food)
        db.session.commit()
        
        return jsonify({"message": "Comida criada com sucesso!"})
    return jsonify({"message": "Dados inválidos"}), 400

@app.route('/foods/<int:user_id>', methods=['GET'])
def get_foods(user_id):

    if user_id != current_user.id:
        return jsonify({"message": "Acesso negado"}), 403
    foods = Food.query.filter_by(user_id=user_id).all()

    if foods:
        return jsonify([{"id": f.id, "name": f.name, "description": f.description, "date": f.date, "included": f.included }for f in foods])
    return jsonify({"message": "Nenhuma comida encontrada"}), 404


if __name__ == '__main__':
    app.run(debug=True)
    from models.user import User
    from models.food import Food