
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix


class Base(DeclarativeBase):
    pass


# Initialize SQLAlchemy with the Base class
db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///oestudio.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "connect_args": {"check_same_thread": False} if "sqlite" in os.environ.get("DATABASE_URL", "sqlite:///oestudio.db") else {}
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return db.session.get(User, int(user_id))


# Initialize database and routes
with app.app_context():
    try:
        # Import models first
        import models
        
        # Create all tables
        db.create_all()
        
        # Import routes last to avoid circular imports
        import routes
        
    except Exception as e:
        app.logger.error(f"Error during app initialization: {str(e)}")
        raise


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
