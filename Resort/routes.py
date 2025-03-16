from flask import  render_template, flash, redirect, url_for
from Resort.models import User, Blog
from Resort.forms import RegisterForm, LoginForm
from Resort import app

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html", title="Home", css="main.css")

@app.route('/about', methods=['GET'])
def about():
    return render_template("about.html", title="About")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == "omarabderhman123@gmail.com" and form.password.data == "123456":
            flash(f'Login Successful for {form.email.data}', 'success') 
            return redirect(url_for('index'))
        else:
            flash(f'Invalid Credentials', 'danger')

    return render_template("login.html", title="Login", form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        flash(f'An Account created for {form.name.data}', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", title="Register", form=form)