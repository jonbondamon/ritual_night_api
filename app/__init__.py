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

    #from app.routes.user_item_mangement import user_item_management
    #app.register_blueprint(user_item_management)

    #from app.routes.store_management import store_management
    #app.register_blueprint(store_management)

    #from app.routes.item_management import item_management
    #app.register_blueprint(item_management)

    #from app.routes.item_type_management import item_type_management
    #app.register_blueprint(item_type_management)

    #from app.routes.rarity_type_management import rarity_type_management
    #app.register_blueprint(rarity_type_management)

    #from app.routes.chroma_management import chroma_management
    #app.register_blueprint(chroma_management)

    #from app.routes.shader_management import shader_management
    #app.register_blueprint(shader_management)

    #from app.routes.xp_booster_management import xp_booster_management
    #app.register_blueprint(xp_booster_management)

    #from app.routes.booster_type_management import booster_type_management
    #app.register_blueprint(booster_type_management)

    #from app.routes.referral_management import referral_management
    #app.register_blueprint(referral_management)

    #from app.routes.item_bundle_management import item_bundle_management
    #app.register_blueprint(item_bundle_management)

    #from app.routes.premium_store_set_management import premium_store_set_management
    #app.register_blueprint(premium_store_set_management)

    #from app.routes.premium_store_schedule_management import premium_store_schedule_management
    #app.register_blueprint(premium_store_schedule_management)



    return app
