from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
import uuid
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request
from flask import jsonify
from flask_migrate import Migrate
import datetime

# initialize app

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'gaidi'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://developer:developerwilson@localhost/bucketlist'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password = db.Column(db.String(250))
    admin = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    bucketlist = db.relationship('Bucketlist', backref='user', lazy='dynamic')


class Bucketlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    text = db.Column(db.String(100))
    complete = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


@app.route('/user', methods=['GET'])
def get_all_users():
    users = User.query.all()
    output = []

    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['email'] = user.email
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        user_data['created_at'] = user.created_at
        output.append(user_data)

    return jsonify(output)


@app.route('/user/<public_id>', methods=['GET'])
def get_one_user(public_id):

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    user_data = {}
    user_data['id'] = user.id
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['email'] = user.email
    user_data['password'] = user.password
    user_data['admin'] = user.admin

    return jsonify(user_data)


@app.route('/user/create', methods=['POST'])
def create_user():
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(public_id=str(uuid.uuid4()),
                    name=data['name'], password=hashed_password, admin=False, email=data['email'])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'New User Created!'})


@app.route('/user/login', methods=['POST'])  # login user
def login_user():
    auth = request.get_json()
    user = User.query.filter_by(email=auth['email']).first()

    if not user:
        return jsonify({'message': 'No user found!'})
        # status = False
    else:
        if check_password_hash(user.password, auth['password']):
            session['logged_in'] = True
            token = user.public_id
            return jsonify({'token': token})
            # return jsonify({'message': 'User logged in!'})
            # status = True
        else:
            return jsonify({'message': 'Wrong password!'})

    # if check_password_hash(user.password, auth['password']):
    #     token = user.public_id
    #     return jsonify({'token': token})

    # return jsonify({'message': 'Wrong Password!'})


@app.route('/user/logout', methods=['GET'])  # logout user
def logout_user():
    session.clear()
    return jsonify({'message': 'User logged out!'})


@app.route('/user/<public_id>', methods=['DELETE'])
def delete_user(public_id):

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'The user has been deleted!'})

# todos!!!!


@app.route('/bucketlist', methods=['GET'])
def todos():
    todos = Bucketlist.query.all()

    output = []

    for todo in todos:
        todo_data = {}
        todo_data['title'] = todo.title
        todo_data['id'] = todo.id
        todo_data['user_id'] = todo.user_id
        todo_data['text'] = todo.text
        todo_data['complete'] = todo.complete
        todo_data['created_at'] = todo.created_at
        output.append(todo_data)

    return jsonify(output)


# get all todos for a specific user (user_id)
@app.route('/bucketlist/<user_id>/user', methods=['GET'])
def get_todos(user_id):

    # get all todos for a specific user (user_id)
    todos = Bucketlist.query.filter_by(user_id=user_id).all()
    # create an empty list
    output = []

    for todo in todos:
        todo_data = {}
        todo_data['title'] = todo.title
        todo_data['id'] = todo.id
        todo_data['user_id'] = todo.user_id
        todo_data['text'] = todo.text
        todo_data['complete'] = todo.complete
        todo_data['created_at'] = todo.created_at
        output.append(todo_data)

    return jsonify(output)


@app.route('/bucketlist/<todo_id>', methods=['GET'])
def get_one_todo(todo_id):
    todo = Bucketlist.query.filter_by(id=todo_id).first()

    if not todo:
        return jsonify({'message': 'No todo Found!'})

    todo_data = {}
    todo_data['title'] = todo.title
    todo_data['id'] = todo.id
    todo_data['text'] = todo.text
    todo_data['complete'] = todo.complete

    return jsonify(todo_data)


@app.route('/bucketlist', methods=['POST'])  # create a todo
def create_todo():

    data = request.get_json()

    new_todo = Bucketlist(
        text=data['text'], user_id=data['user_id'], title=data['title'], complete=False)
    db.session.add(new_todo)
    db.session.commit()

    return jsonify({'message': "Todo has been created!"})


@app.route('/bucketlist/<todo_id>', methods=['PUT'])
def complete_todo(todo_id):

    todo = Bucketlist.query.filter_by(id=todo_id).first()

    if not todo:
        return jsonify({'message': 'No todo Found!'})

    todo.complete = True

    db.session.commit()

    return jsonify({'message': 'To do item has been completed!'})


# update a todo
@app.route('/bucketlist/<todo_id>/update', methods=['PUT'])
def update_todo(todo_id):

    data = request.get_json()

    todo = Bucketlist.query.filter_by(id=todo_id).first()

    if not todo:
        return jsonify({'message': 'No todo Found!'})

    todo.text = data['text']
    todo.title = data['title']
    todo.complete = data['complete']

    db.session.commit()

    return jsonify({'message': 'To do item has been updated!'})


@app.route('/bucketlist/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Bucketlist.query.filter_by(id=todo_id).first()

    if not todo:
        return jsonify({'message': 'No todo Found!'})
    db.session.delete(todo)
    db.session.commit()

    return jsonify({'message': 'Todo item deleted!'})


if __name__ == "__main__":
    app.run()
