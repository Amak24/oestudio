from app import app

# Import routes and models to register them with the app
# These imports must happen after app initialization
try:
    import routes
    import models
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")

# Make sure the app is available for Gunicorn to import
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)