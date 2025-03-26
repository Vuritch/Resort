from flask import Flask
from Resort.models import db, User, Booking

app = Flask(__name__, 
    template_folder='Resort/templates',
    static_folder='Resort/static')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:omar@localhost/resort?charset=utf8mb4'
app.config["SECRET_KEY"] = "123456789"

db.init_app(app)

from Resort.routes import *

if __name__ == '__main__':
    with app.app_context():
            db.create_all()            
    app.run('127.0.0.5', debug=True)
