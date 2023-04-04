from flask import Flask, jsonify, request, render_template, redirect,url_for
import jwt
import datetime
import mysql.connector
import os
import uuid
from werkzeug.utils import secure_filename
from flask import send_from_directory


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB
public_items = ['public_item1', 'public_item2', 'public_item3']

# Connect to the database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="449_DB"
)


# Define a function to handle errors
def error_response(message, status_code):
    response = {
        'error': {
            'message': message,
            'status': status_code
        }
    }
    return response, status_code

# Error handlers
@app.errorhandler(400)
def bad_request_error(error):
    message = "The server could not understand the request due to invalid syntax."
    return error_response(message, 400)

@app.errorhandler(401)
def unauthorized_error(error):
    message = "You are not authorized to access this resource."
    return error_response(message, 401)

@app.errorhandler(404)
def not_found_error(error):
    message = "The requested resource was not found on the server."
    return error_response(message, 404)

@app.errorhandler(500)
def internal_server_error(error):
    message = "The server encountered an internal error and was unable to complete your request."
    return error_response(message, 500)
        

# User model
class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

# Sample user data
users = [
    User('user1', 'password1'),
    User('user2', 'password2')
]

# Authentication function
def authenticate(username, password):
    for user in users:
        if user.username == username and user.password == password:
            return user

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)

        # Authenticate user
        user = authenticate(username, password)
        if not user:
            return jsonify({'message': 'Invalid username or password'}), 401

        # Generate JWT token
        token = jwt.encode({
            'user_id': user.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'])

        return redirect('/upload')
    
    # Serve login page
    return render_template('login.html')

# Protected route
@app.route('/protected')
def protected():
    token = request.headers.get('Authorization', None)
    if not token:
        return jsonify({'message': 'Missing authorization header'}), 401

    # Decode token
    try:
        token = token.split(' ')[1]
        data = jwt.decode(token, app.config['SECRET_KEY'])
    except:
        return jsonify({'message': 'Invalid token'}), 401

    return jsonify({'message': 'Protected data'})

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_file_extension(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower()

@app.route('/upload', methods=['POST','GET'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        print(request.files)
        if 'file' not in request.files:
            return jsonify({'message': 'No file part'}), 400
        file = request.files['file']
        print(file)
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_extension = get_file_extension(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return jsonify({'message': 'File uploaded successfully'})
        else:
            return jsonify({'message': 'File type not allowed'}), 400
    return render_template('upload.html')


# Public endpoint
@app.route('/public')
def public():
    return public_items

# Index route
@app.route('/')
def index():
    return render_template('index.html', items=public_items)

if __name__ == '__main__':
    app.run(debug=True)
