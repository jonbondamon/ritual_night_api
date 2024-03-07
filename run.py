from app import create_app
from waitress import serve
from dotenv import load_dotenv
import os

load_dotenv()
app = create_app()

if __name__ == '__main__':

    host = '127.0.0.1'

    if os.getenv('FLASK_ENV') == 'development':
        host = '127.0.0.1'
    elif os.getenv('FLASK_ENV') == 'production':
        host = '0.0.0.0'

    serve(app, host=host, port=5000)
