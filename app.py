#ET/2018/045
from functools import wraps
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import processor
import mysql.connector
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = 'enter-a-very-secretive-key-3479373'

con = mysql.connector.connect(user='saru', password='password', host='localhost', database='admin_chatbot')

@app.route('/login', methods=["GET", "POST"])
def login():
    if 'username' in session and session['role'] == 'student':
        return redirect(url_for('index'))
    elif 'username' in session and session['role'] == 'lecturer':
        return redirect(url_for('lecturer'))
    elif 'username' in session and session['role'] == 'admin':
        return redirect(url_for('admin'))
    else:
        return render_template('login.html', **locals()) 

@app.route('/', methods=["GET", "POST"])
def index():
    if 'username' in session and session['role'] == 'student':
        return render_template('index.html', **locals())
    else:
        return redirect(url_for('login'))

@app.route('/lecturer', methods=["GET", "POST"])
def lecturer():
    if 'username' in session and session['role'] == 'lecturer':
        return render_template('lecturers.html', **locals())
    else:
        return redirect(url_for('login'))

@app.route('/admin', methods=["GET", "POST"])
def admin():
    if 'username' in session and session['role'] == 'admin':
        return render_template('admin.html', **locals())
    else:
        return redirect(url_for('login'))

@app.route('/chatbot', methods=["GET", "POST"])
def chatbotResponse():
    if request.method == 'POST':
        question = request.form['question']
        response = processor.chatbot_response(question)
    return jsonify({"response": response })

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    cursor = con.cursor()
    hashed_password = hashlib.sha256(data['password'].encode()).hexdigest()
    cursor.execute('INSERT INTO users (firstname, lastname, username, password, phone, role) VALUES (%s, %s, %s, %s, %s, %s)', (data['firstname'], data['lastname'], data['username'], hashed_password, data['phone'], data['role']))
    con.commit()

    return 'Data saved successfully'

@app.route('/update', methods=['POST'])
def update():
    data = request.get_json()
    cursor = con.cursor()
    hashed_password = hashlib.sha256(data['password'].encode()).hexdigest()
    cursor.execute('UPDATE users SET firstname = %s, lastname = %s, username = %s, password = %s, phone = %s, role = %s WHERE id = %s', (data['firstname'], data['lastname'], data['username'], hashed_password, data['phone'], data['role'], data['id']))
    con.commit()

    return 'Data updated successfully'

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    cursor = con.cursor()
    cursor.execute('DELETE FROM users WHERE id = %s', (id,))
    con.commit()

    return 'Data deleted successfully'

@app.route('/user', methods=['GET', 'POST'])
def user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        cursor = con.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, hashed_password))
        user = cursor.fetchone()

        if user:
            session['username'] = user[3]
            session['firstname'] = user[1]
            session['lastname'] = user[2]
            session['role'] = user[6]

            if session['role'] == 'student':
                return redirect(url_for('index'))
            if session['role'] == 'lecturer':
                return redirect(url_for('lecturer'))
            if session['role'] == 'admin':
                return redirect(url_for('admin'))
            return redirect(url_for('login'))
        else:
            return redirect(url_for('login'))
    return '''login page'''

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
