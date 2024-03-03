from flask import Flask
from flasgger import Swagger

def create_app():
    app = Flask(__name__)
    app.config['SWAGGER'] = {
        'title': 'Ritual Night API',
        'uiversion': 3
    }
    Swagger(app)

    from routes.user_management import user_management
    app.register_blueprint(user_management)

    return app
