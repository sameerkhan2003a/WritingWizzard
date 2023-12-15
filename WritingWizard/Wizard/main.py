from flask import Flask, render_template, request, session, flash, redirect, url_for
import os
import openai
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import json



app = Flask(__name__)

secret = secrets.token_urlsafe(32)
app.secret_key = secret  # set the secret key

def save_users(users):
    with open('users3.json', 'w') as f:
        json.dump(users, f)

def load_users():
    try:
        with open('users3.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

users = load_users()

# This function checks if the user is logged in
def is_logged_in():
    return 'username' in session

@app.route('/index', methods=['GET', 'POST'])
def index():
    if not is_logged_in():
        flash('You need to log in first.')
        return redirect(url_for('Login'))

    result = None 
    if request.method == 'POST':
        essayLength = request.form['essayLength']
        essayQuality = request.form['essayQuality']
        essayTopic = request.form['essayTopic']

        client = openai.OpenAI(api_key='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')
     
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            temperature=0,
            max_tokens=1000,
            messages=[
                    {"role": "system", "content": f"You are a Writing Wizard who writes essays precisely of {essayLength} size or length and of {essayQuality} quality focused totally on the topic, finally be friendly with the user and do your job as perfectly as possible, Seperate the essay completely from your wizard intro, Be unbiased."},
               { "role": "user", "content":  essayTopic},
            ]
        )
        result = response.choices[0].message.content
        

    return render_template('index.html', result=result)

@app.route('/about', methods=['GET', 'POST'])
def about():
    if not is_logged_in():
        flash('You need to log in first.')
        return redirect(url_for('Login'))
    return render_template('about.html')

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/SignUp', methods=['GET', 'POST'])
def SignUp():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        rePassword = request.form['rePassword']

        # Check if passwords match
        if password != rePassword:
            error = 'Passwords do not match! Please try again.'
        elif username in users:  # Check if username already exists
            error = 'Username already exists! Please choose a different username.'
        else:
            # Store the username and hashed password
            users[username] = generate_password_hash(password)
            save_users(users)  # Save users to file
            flash('Signup successful! You can now log in.')
            return redirect(url_for('Login'))  # Redirect to login page after successful signup

    return render_template('SignUp.html', error=error)


@app.route('/Login', methods=['GET', 'POST'])
def Login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username exists and password is correct
        if username in users and check_password_hash(users[username], password):
            session['username'] = username  # log the user in by setting a session variable
            return redirect(url_for('index'))  # Redirect to index page after successful login
        else:
            error = 'Invalid username or password! Please try again.'
    return render_template('Login.html', error=error)

@app.route('/navbar', methods=['GET', 'POST'])
def navbar():
    return render_template('navbar.html')

@app.route('/Logout')
def Logout():
    session.pop('username', None)  # Clear the 'username' key from the session
    flash('You have been logged out.')
    return redirect(url_for('Login'))

if __name__ == '__main__':
    app.run(debug=True)
