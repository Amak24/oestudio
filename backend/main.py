
from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

# Make sure the app is available for Gunicorn to import
application = app
