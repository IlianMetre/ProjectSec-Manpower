# Imports
from flask import Flask
import website.db_connect as db_connect
from werkzeug.middleware.proxy_fix import ProxyFix

# Function to create and configure the Flask application
def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = 'ProjectSec@IP2'

     # Connect to the database and obtain the configuration
    config = db_connect.connect_to_database()

    # Configure the app to handle proxy headers for correct URL handling when behind a reverse proxy
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)

    # Import and register the authentication blueprints
    from .auth import auth

    # Register the auth blueprint with URL prefix
    app.register_blueprint(auth, url_prefix='/')

    return app