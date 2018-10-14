from flask import Flask, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager , login_required , UserMixin , login_user
import os, sys


app = Flask(__name__)
app.secret_key = "123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
'''
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return models.user.user_with_id(id)

@app.before_request
def before_request():
    g.user = current_user
'''
	
s_pet_types = [  # array of pet types
        { 
            'pet_type': "magma frog", 
            'price': 5,
			'filename': "MagmaFrog" 
        },
        { 
            'pet_type': "green frog", 
            'price': 2,
			'filename': "GreenFrog"
        },
        { 
            'pet_type': "chocolate frog", 
            'price': 1,
			'filename': "ChocolateFrog" 
        },
        { 
            'pet_type': "stripy cat", 
            'price': 15,
			'filename': "stripycat"
        },
        { 
            'pet_type': "fox", 
            'price': 50,
			'filename': "Fox"
        },
		{ 
            'pet_type': "elephant", 
            'price': 120,
			'filename': "elephant"
        },
		{ 
            'pet_type': "caterpillar", 
            'price': 10,
			'filename': "caterpillar"
		},
		{ 
            'pet_type': "Dragon", 
            'price': 75,
			'filename': "Dragon"
		},
		{ 
            'pet_type': "snake", 
            'price': 26,
			'filename': "snake"
		},
		{ 
            'pet_type': "pumpkin", 
            'price': 50,
			'filename': "Pumpkin"
		},
		{ 
            'pet_type': "feathered conker", 
            'price': 7,
			'filename': "FeatheredConker"
		},
		{ 
            'pet_type': "witch", 
            'price': 500,
			'filename': "Witch"
		},
    ]

def pet_types():
	types = [pet["pet_type"] for pet in s_pet_types]
	return types

def pet_from_type(given_type):
	if given_type in pet_types():
		pet = [pet for pet in s_pet_types if pet["pet_type"]==given_type]
		if len(pet):
			return pet[0]
	return None

def pet_filename(given_type):
	pet = pet_from_type(given_type)
	if pet:
		return pet["filename"] + '.png'
	return None

class User(db.Model):
	""" Create user table"""
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	password = db.Column(db.String(80))
	gold = db.Column(db.Integer())

	def __init__(self, username, password):
		self.username = username
		self.password = password
		self.gold = 1

	def get_id(self):
		return self.id

	def is_active(self):
		return True

	def get_auth_token(self):
		return make_secure_token(self.username , key='secret_key')

class Pet(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	owner = db.Column(db.Integer())
	name = db.Column(db.String(80))
	price = db.Column(db.Integer())
	pet_type = db.Column(db.String(80))

	def __init__(self, owner, name, price, pet_type):
		self.owner = owner
		self.name = name
		self.price = price
		self.pet_type = pet_type

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

@app.route('/', methods=['GET', 'POST'])
def home():
	""" Session control"""
	if not session.get('logged_in'):
		return render_template('index.html')
	else:
		print(session.get('gold'))
		return render_template('index.html', data=session.get('gold'))
		#if request.method == 'POST':
		#return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
	"""Login Form"""
	if request.method == 'GET':
		return render_template('login.html')
	else:
		name = request.form['username']
		passw = request.form['password']
		try:
			data = User.query.filter_by(username=name, password=passw).first()
			if data is not None:
				print(data)
				print(data.username)
				print(data.gold)
				session['logged_in'] = True
				session['gold'] = data.gold
				session['username'] = data.username
				session['userid'] = data.id
				return redirect(url_for('home'))
			else:
				return 'Not Logged In 1'
		except:
			print(sys.exc_info())
			return "Not Logged In"

@app.route('/register/', methods=['GET', 'POST'])
def register():
	"""Register Form"""
	if request.method == 'POST':
		new_user = User(username=request.form['username'], password=request.form['password'])
		db.session.add(new_user)
		db.session.commit()
		return render_template('login.html')
	return render_template('register.html')

@app.route("/logout")
def logout():
	"""Logout Form"""
	session['logged_in'] = False
	session.pop('gold', None)
	return redirect(url_for('home'))

@app.route("/pets")
def pets():
	"""Pets overview"""
	if session['logged_in'] == True :
		print(session['userid'])
		#data = Pet.query.all()
		data = Pet.query.filter_by(owner=session['userid'])
		files = []
		for d in data: 
			filename = pet_filename(d.pet_type)
			files = files + [filename]

		print(files)
		print(data)
		if data is not None:
			return render_template('pets.html', pets=zip(data, files))
	return redirect(url_for('login'))

@app.route("/pets/create", methods=['GET', 'POST'])
def pets_create():
	"""Pet creation"""
	if session['logged_in'] == True :
		if request.method == 'POST':

			pet = pet_from_type(request.form['pet_type'])
			if pet:
				pet_price = pet["price"]
				new_pet = Pet(owner=session["userid"], 
					name=request.form['pet_name'], 
					pet_type = request.form['pet_type'], 
					price = pet_price)
			db.session.add(new_pet)
			db.session.commit()
		else:
			return render_template('pets_create.html', pets = s_pet_types)
	return redirect(url_for('pets'))


if __name__ == '__main__':
	app.debug = True
	db.create_all()
	app.run(host='0.0.0.0')
	