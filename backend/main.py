from app import app
from routes import *  # Import all routes
from models import *  # Import all models

# Make sure the app is available for Gunicorn to import
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)