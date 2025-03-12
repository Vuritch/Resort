from flask import Flask, render_template, flash, url_for, redirect
from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = "b339f8784e4baa72e389743af5b2ddbfa4271aa615838d7fec426f1aa6530955"

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html", title="Home", css="main.css")

@app.route('/about', methods=['GET'])
def about():
    return render_template("about.html", title="About")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():  # Call the method
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
        return redirect(url_for('index'))
    return render_template("register.html", title="Register", form=form)

if __name__ == "__main__":
    app.run(debug=True)
