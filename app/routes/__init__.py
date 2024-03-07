from functools import wraps
from flask import request, jsonify
import jwt, os
from app.models import Session, Token

SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ALGORITHM = os.getenv('JWT_ALGORITHM')

def role_required(required_roles):
    if not isinstance(required_roles, list):
        required_roles = [required_roles]

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
            else:
                return jsonify({'message': 'Token is missing or invalid'}), 401

            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                session = Session()
                token_record = session.query(Token).filter_by(jti=payload['jti']).first()

                if not token_record:
                    return jsonify({'message': 'Token is invalid or expired'}), 401

                user_roles = payload.get('roles', [])
                if not set(required_roles).intersection(user_roles):
                    return jsonify({'message': 'Access denied: Required role(s) not found'}), 403
                
                # Attach user_id from the token payload to Flask's global object or directly to request
                request.user_id = payload['user_id']
                request.jti = payload['jti']
            except Exception as e:
                return jsonify({'message': 'Token is invalid', 'error': str(e)}), 401
            finally:
                if session:
                    session.close()

            return f(*args, **kwargs)
        return decorated_function
    return decorator

user_role_required = role_required('user')
admin_role_required = role_required('admin')
