from flask import Flask
from Resort.models import db, User, Room, RoomType, ExtraService, Booking, BookingExtraService
from flask_login import LoginManager
from Resort import admin 
from wtforms.validators import Optional
import os

app = Flask(__name__, 
    template_folder='Resort/templates',
    static_folder='Resort/static')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:omar@localhost/resort1?charset=utf8mb4'
app.config["SECRET_KEY"] = "123456789"

UPLOAD_FOLDER = os.path.join(app.static_folder, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif'}
def allowed_file(filename):
    return (
      '.' in filename and
      filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS
    )
# Initialize database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please login to access the booking page.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from Resort.routes import *

if __name__ == '__main__':
    with app.app_context():
            
            db.create_all()            
    app.run(debug=True)
