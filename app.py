from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import uuid

from werkzeug.security import generate_password_hash,check_password_hash
from flask import request
from flask import jsonify
from flask_migrate import Migrate


 
 #initialize app

app = Flask(__name__)

app.config['SECRET_KEY'] ='gaidi'
app.config['SQLALCHEMY_DATABASE_URI']= 'postgresql+psycopg2://moringa:Access@localhost/bucketlist1'

 
db = SQLAlchemy(app) 
Migrate(app,db)

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    public_id=db.Column(db.String(50),unique=True)
    name = db.Column(db.String(50))
    password=db.Column(db.String(250))
    admin=db.Column(db.Boolean)
    bucketlist = db.relationship('Bucketlist', backref='user', lazy='dynamic')
    
    
    
class Bucketlist(db.Model):
    id=db.Column(db.Integer,primary_key=True)   
    title=db.Column(db.String(100)) 
    text = db.Column(db.String(100))
    complete=db.Column(db.Boolean)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))


    
@app.route('/user',methods=['GET'])
def get_all_users():
    users = User.query.all()
    output = []
    
    for user in users:
        user_data ={}
        user_data['public_id'] = user.public_id
        user_data['name'] =user.name
        user_data['password']=user.password
        user_data['admin'] =user.admin
        output.append(user_data)
        
    return jsonify({'users':output})

@app.route('/user/<public_id>',methods=['GET']) 
def get_one_user(public_id):
    
    user = User.query.filter_by(public_id=public_id).first()
    
    if not user:
        return jsonify({'message':'No user found!'})
    
    
    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] =user.name
    user_data['password']=user.password
    user_data['admin'] =user.admin
    
    return jsonify({'user':user_data})
    
    
    
    

@app.route('/user/',methods=['POST'])
def create_user():
    data =request.get_json()
    
    hashed_password=generate_password_hash(data['password'],method='sha256')
    new_user=User(public_id=str(uuid.uuid4()),name=data['name'],password=hashed_password,admin=False)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify ({'message':'New User Created!'})


    

@app.route('/user/<public_id>',methods=['DELETE'])
def delete_user(public_id):
    
    user = User.query.filter_by(public_id=public_id).first()
    
    if not user:
        return jsonify({'message':'No user found!'})
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message':'The user has been deleted!'})

#todos!!!!

@app.route('/bucketlist',methods=['GET'])
def todos():
    todos = Bucketlist.query.all()
    
    output=[]
    
    for todo in todos:
        todo_data={}
        todo_data['title']=todo.title
        todo_data ['id']=todo.id
        todo_data ['user_id']=todo.user_id
        todo_data['text']=todo.text
        todo_data['complete']=todo.complete
        output.append(todo_data)
        
    return jsonify({'todos': output})

@app.route('/bucketlist/<user_id>/user',methods=['GET'])
def get_todos_by_user(user_id):
    
    todos=Bucketlist.query.filter_by(user_id=user_id).all()
    
    if not todos:
        return jsonify({'message':'No todo Found!'})
    todo_data={}
    
    for todo in todos:
        todo_data['title']=todo.title
        todo_data ['id']=todo.id
        todo_data['text']=todo.text
        todo_data['complete']=todo.complete
    
        

    
    
    
    
    
    return jsonify(todo_data)
    
    
    


@app.route('/bucketlist/<todo_id>',methods=['GET'])
def get_one_todo(todo_id):
    todo=Bucketlist.query.filter_by(id=todo_id).first()
    
    if not todo:
        return jsonify({'message':'No todo Found!'})
    
    todo_data={}
    todo_data['title']=todo.title
    todo_data ['id']=todo.id
    todo_data['text']=todo.text
    todo_data['complete']=todo.complete
    
    
    return jsonify(todo_data)
    
    
    
    

@app.route('/bucketlist',methods=['POST'])
def create_todo():
    
    data =request.get_json()
    
    new_todo= Bucketlist(text=data['text'],user_id=data['user_id'],title=data['title'],complete=False)
    db.session.add(new_todo)
    db.session.commit()
     
    return jsonify({'message':"Todo has been created!"})

@app.route('/bucketlist/<todo_id>',methods=['PUT'])
def complete_todo(todo_id):
    
    todo=Bucketlist.query.filter_by(id=todo_id).first()
    
    if not todo:
        return jsonify({'message':'No todo Found!'})
    
    todo.complete=True
    
    db.session.commit()
    
    
    
    
    
    return jsonify({'message':'To do item has been completed!'})

@app.route('/bucketlist/<todo_id>',methods=['DELETE'])
def delete_todo(todo_id):
    todo=Bucketlist.query.filter_by(id=todo_id).first()
    
    if not todo:
        return jsonify({'message':'No todo Found!'})
    db.session.delete(todo)
    db.session.commit()
    
    
    return jsonify({'message':'Todo item deleted!'})
    
    

  
    
    
    
     





if __name__=="__main__":
    app.run()