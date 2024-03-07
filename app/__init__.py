from flask import Flask
from flasgger import Swagger

def create_app():
    app = Flask(__name__)
    app.config['SWAGGER'] = {
        'title': 'Ritual Night API',
        'uiversion': 3,
        'specs_route': '/apidocs/',
        'securityDefinitions': {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': 'Enter your bearer token in the format "Bearer <token>"'
            }
        },
        'security': [{'Bearer': []}]
    }
    
    swagger = Swagger(app)

    from app.routes.user_management import user_management
    app.register_blueprint(user_management)

    from app.routes.user_item_mangement import user_item_management
    app.register_blueprint(user_item_management)

    from app.routes.store import store
    app.register_blueprint(store)

    return app
