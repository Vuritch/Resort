from flask import Flask
from Resort.models import db, User, Booking
from flask_login import LoginManager

app = Flask(__name__, 
    template_folder='Resort/templates',
    static_folder='Resort/static')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:omar@localhost/resort?charset=utf8mb4'
app.config["SECRET_KEY"] = "123456789"

# Initialize database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from Resort.routes import *

if __name__ == '__main__':
    with app.app_context():
            db.create_all()            
    app.run(debug=True)
