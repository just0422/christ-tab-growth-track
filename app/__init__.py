from flask import Flask
from flask_mail import Mail

from . import constants


app = Flask(__name__)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'saintschurchnoreply@gmail.com'
app.config['MAIL_PASSWORD'] = 'kyxqgvexqdoaejsa'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = 'sainstchurchnoreply@gmail.com'

app.config['SERVER_NAME'] = '206.189.177.49'

# mail.init_app(app)
mail = Mail(app)
    
from app import main
