from app.routes import SECRET_KEY, ALGORITHM, user_role_required, admin_role_required
from flask import Blueprint, request, jsonify
from app.models import Session, User, Token, Stat, UserItem, Item, Referral, XPBooster
import bcrypt, datetime, jwt, uuid

user_management = Blueprint('user_management', __name__, url_prefix='/api')

@user_management.route('/user/register', methods=['POST'])
def register_user():
    """
    Register a new user.
    This endpoint registers a new user.
    ---
    tags:
      - User Management
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        description: User's registration data
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              description: The username of the user.
            email:
              type: string
              description: The email of the user.
            password:
              type: string
              description: The password of the user.
    responses:
      200:
        description: User registered successfully.
      400:
        description: Missing required fields.
      409:
        description: User with this username or email already exists.
      500:
        description: Internal server error.
    """
    session = Session()
    try:
        # Extract registration details from the request
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # Validate the presence of required fields
        if not username or not email or not password:
            return jsonify({'error': 'Missing required fields'}), 400

        # Check if the user already exists to prevent duplicates
        existing_user = session.query(User).filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            return jsonify({'error': 'User with this username or email already exists'}), 409

        # Hash the password with bcrypt
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Instantiate a new User object with the hashed password
        new_user = User(username=username, email=email, password_hash=password_hash.decode('utf-8'))

        # Persist the new user to the database
        session.add(new_user)
        session.commit()

        return jsonify({'success': 'User registered successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()
    
@user_management.route('/user/login', methods=['POST'])
def authenticate_user():
    """
    User Login
    This endpoint logs in a user.
    ---
    tags:
      - User Management
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        description: User's login credentials
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              description: The user's email
              default: johndoe@example.com
            password:
              type: string
              description: The user's password
              default: password123
    responses:
      200:
        description: User authenticated successfully
        examples:
          application/json: {"success": "User authenticated successfully", "token": "<token_here>"}
      401:
        description: Invalid email or password
        examples:
          application/json: {"error": "Invalid email or password"}
      500:
        description: Internal server error
        examples:
          application/json: {"error": "An unexpected error occurred"}
    """
    session = Session()
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        # Validate the presence of required fields
        if not email or not password:
            return jsonify({'error': 'Missing email or password'}), 400

        # Find user by email
        user = session.query(User).filter_by(email=email).first()

        # Check if user exists and password is correct
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            # Authentication successful, generate token
            jti = str(uuid.uuid4())  # Generate a unique JWT ID
            token_data = {
                "jti": jti,
                "user_id": user.user_id,
                "email": user.email,
                "username": user.username,
                "roles": ["user"],
                "ip": request.remote_addr,  # Store client's IP address
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # Token expires in 24 hours
            }
            token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

            # Store the JTI in the database
            token_record = Token(jti=jti)
            session.add(token_record)
            session.commit()

            return jsonify({'success': 'User authenticated successfully', 'token': token}), 200
        else:
            # Authentication failed
            return jsonify({'error': 'Invalid username or password'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@user_management.route('/user', methods=['GET'])
@user_role_required
def get_user():
    """
    Get User
    This endpoint returns the authenticated user's details, including their stats, items, money, XP boosters, and general store items they don't own.
    ---
    tags:
      - User Management
    security:
      - Bearer: []
    consumes:
      - application/json
    responses:
      200:
        description: User details fetched successfully.
        schema:
          type: object
          properties:
            user_id:
              type: integer
              description: The user's ID.
            username:
              type: string
              description: The user's username.
            email:
              type: string
              description: The user's email.
            gold_amount:
              type: integer
              description: The amount of gold the user has.
            silver_amount:
              type: integer
              description: The amount of silver the user has.
            stats:
              type: object
              properties:
                minigames_completed:
                  type: integer
                  description: The number of mini-games the user has completed.
                games_won:
                  type: integer
                  description: The number of games the user has won.
                rituals_completed:
                  type: integer
                  description: The number of rituals the user has completed.
            items:
              type: array
              items:
                $ref: '#/definitions/Item'
            xp_boosters:
              type: array
              items:
                $ref: '#/definitions/XPBooster'
            general_store_items:
              type: array
              items:
                $ref: '#/definitions/GeneralStoreItem'
      404:
        description: User not found.
        examples:
          application/json: {"error": "User not found"}
      500:
        description: Internal server error.
        examples:
          application/json: {"error": "An unexpected error occurred"}
    definitions:
      Item:
        type: object
        properties:
          item_id:
            type: integer
            description: The item's ID.
          item_name:
            type: string
            description: The item's name.
          item_level:
            type: integer
            description: The item's level.
          item_xp:
            type: integer
            description: The item's XP.
          prestige_level:
            type: integer
            description: The item's prestige level.
          selected_chroma_id:
            type: integer
            description: The selected chroma ID for the item.
          selected_shader_id:
            type: integer
            description: The selected shader ID for the item.
          favorite:
            type: boolean
            description: Whether the item is a favorite.
          is_equipped:
            type: boolean
            description: Whether the item is equipped.
      XPBooster:
        type: object
        properties:
          booster_id:
            type: integer
            description: The booster's ID.
          booster_effect:
            type: integer
            description: The effect of the booster.
          is_active:
            type: boolean
            description: Whether the booster is currently active.
          games_applied:
            type: integer
            description: The number of games the booster has been applied to.
      GeneralStoreItem:
        type: object
        properties:
          item_id:
            type: integer
            description: The item's ID.
          item_name:
            type: string
            description: The item's name.
          silver_cost:
            type: integer
            description: The silver cost of the item.
          gold_cost:
            type: integer
            description: The gold cost of the item.
    """
    session = Session()
    try:
        # Use request.user_id to get the user ID from the token directly
        user_id = request.user_id
        # Query the database for the authenticated user
        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            # Serialize stats if available
            stats_info = {
                'minigames_completed': user.stats.minigames_completed if user.stats else 0,
                'games_won': user.stats.games_won if user.stats else 0,
                'rituals_completed': user.stats.rituals_completed if user.stats else 0,
            }
            # Serialize user items
            items_info = [
                {
                    'item_id': item.item.item_id,
                    'item_name': item.item.item_name,
                    'item_level': item.item_level,
                    'item_xp': item.item_xp,
                    'prestige_level': item.prestige_level,
                    'selected_chroma_id': item.selected_chroma_id,
                    'selected_shader_id': item.selected_shader_id,
                    'favorite': item.favorite,
                    'is_equipped': item.is_equipped,
                }
                for item in user.user_items
            ] if user.user_items else []
            # Serialize XP boosters
            xp_boosters_info = [
                {
                    'booster_id': booster.booster_id,
                    'booster_effect': booster.booster_effect,
                    'is_active': booster.is_active,
                    'games_applied': booster.games_applied,
                }
                for booster in user.xp_boosters
            ] if user.xp_boosters else []
            # Get the item IDs of the items the user owns
            user_item_ids = [item.item_id for item in user.user_items]
            # Query the general store items that the user does not own
            general_store_items = session.query(Item).filter(
                Item.is_general_store_item == True,
                ~Item.item_id.in_(user_item_ids)
            ).all()
            # Serialize general store items
            general_store_items_info = [
                {
                    'item_id': item.item_id,
                    'item_name': item.item_name,
                    'silver_cost': item.silver_cost,
                    'gold_cost': item.gold_cost,
                    'unity_name': item.unity_name,
                }
                for item in general_store_items
            ]
            # Construct a response object with user details, including stats, items, money, XP boosters, and general store items
            user_details = {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'gold_amount': user.gold_amount,
                'silver_amount': user.silver_amount,
                'stats': stats_info,
                'items': items_info,
                'xp_boosters': xp_boosters_info,
                'general_store_items': general_store_items_info,
            }
            return jsonify(user_details), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@user_management.route('/user/update/info', methods=['PUT'])
@user_role_required  
def update_user():
    """
    Update User Details
    This endpoint allows the authenticated user to update their details.
    ---
    tags:
      - User Management
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        description: Fields to update
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              description: New username for the user.
            email:
              type: string
              description: New email for the user.
    responses:
      200:
        description: User details updated successfully.
        examples:
          application/json: {"success": "User details updated successfully"}
      400:
        description: Bad request, if required fields are missing in the request body.
        examples:
          application/json: {"error": "Missing required fields"}
      404:
        description: User not found, if no user matches the provided user ID from the token.
        examples:
          application/json: {"error": "User not found"}
      500:
        description: Internal server error, if any exception occurs.
        examples:
          application/json: {"error": "Failed to update user details", "details": "<exception details>"}
    """
    session = Session()
    try:
        user_id = request.user_id  # Get the user ID from the JWT token
        data = request.get_json()  # Assuming the request body contains the fields to update

        # Fetch the user from the database
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Update user fields based on data provided in request
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']

        session.commit()  # Commit changes to the database

        return jsonify({'success': 'User details updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to update user details', 'details': str(e)}), 500
    finally:
        session.close()

@user_management.route('/user/update/password', methods=['PUT'])
@user_role_required
def update_password():
    """
    Update User Password
    This endpoint updates the authenticated user's password.
    ---
    tags:
      - User Management
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        description: New password data
        required: true
        schema:
          type: object
          required:
            - new_password
          properties:
            new_password:
              type: string
              description: The user's new password.
    responses:
      200:
        description: Password updated successfully.
      400:
        description: Missing new password.
      401:
        description: Unauthorized access. Token is missing or invalid.
      500:
        description: Internal server error.
    """
    session = Session()
    try:
        user_id = request.user_id  # Obtained from the JWT token after @user_role_required decorator
        data = request.get_json()
        new_password = data.get('new_password')

        if not new_password:
            return jsonify({'error': 'Missing new password'}), 400

        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Hash the new password with bcrypt
        new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Update the user's password in the database
        user.password_hash = new_password_hash
        session.commit()

        return jsonify({'success': 'Password updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@user_management.route('/user/logout', methods=['POST'])
@user_role_required
def logout_user():
    """
    Logout User
    This endpoint logs out the user by invalidating the JWT token.
    ---
    tags:
      - User Management
    security:
      - Bearer: []
    responses:
      200:
        description: User logged out successfully.
        examples:
          application/json: {"success": "User logged out successfully"}
      401:
        description: Unauthorized access. Token is missing or invalid.
        examples:
          application/json: {"error": "Unauthorized access"}
      500:
        description: Internal server error.
        examples:
          application/json: {"error": "An unexpected error occurred"}
    """
    session = Session()
    try:
        # Extract the token's jti from the request context, set by the @user_role_required decorator
        jti = request.jti  # Assuming the @user_role_required decorator or another mechanism sets request.jti
        # Remove or invalidate the token's jti from the database
        token_record = session.query(Token).filter_by(jti=jti).first()
        if token_record:
            session.delete(token_record)
            session.commit()
            return jsonify({'success': 'User logged out successfully'}), 200
        else:
            return jsonify({'error': 'Token not found or already invalidated'}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to log out', 'details': str(e)}), 500
    finally:
        session.close()

@user_management.route('/user/update/stats', methods=['PUT'])
@user_role_required
def update_user_stats():
    """
    Update User Stats
    This endpoint allows the authenticated user to update their stats by adding the provided values to the existing stats.
    ---
    tags:
      - User Management
    security:
      - Bearer: []
    parameters:
      - in: query
        name: minigames_completed
        required: false
        type: integer
        description: Increment to the total number of minigames completed by the user.
      - in: query
        name: games_won
        required: false
        type: integer
        description: Increment to the total number of games won by the user.
      - in: query
        name: rituals_completed
        required: false
        type: integer
        description: Increment to the number of rituals the user has completed.
    responses:
      200:
        description: User stats updated and new stats returned successfully.
        schema:
          type: object
          properties:
            minigames_completed:
              type: integer
              description: The new total number of minigames completed by the user.
            games_won:
              type: integer
              description: The new total number of games won by the user.
            rituals_completed:
              type: integer
              description: The new number of rituals the user has completed.
      400:
        description: Bad request, if required fields are missing or invalid.
      404:
        description: User not found.
      500:
        description: Internal server error, if any exception occurs.
    """
    session = Session()
    try:
        user_id = request.user_id
        user_stats = session.query(Stat).filter_by(user_id=user_id).first()

        if not user_stats:
            return jsonify({'error': 'User stats not found'}), 404

        # Update stats based on the query parameters
        minigames_completed = request.args.get('minigames_completed', type=int)
        games_won = request.args.get('games_won', type=int)
        rituals_completed = request.args.get('rituals_completed', type=int)

        if minigames_completed is not None:
            user_stats.minigames_completed += minigames_completed
        if games_won is not None:
            user_stats.games_won += games_won
        if rituals_completed is not None:
            user_stats.rituals_completed += rituals_completed

        session.commit()

        # Return the updated stats
        updated_stats = {
            'minigames_completed': user_stats.minigames_completed,
            'games_won': user_stats.games_won,
            'rituals_completed': user_stats.rituals_completed
        }

        return jsonify({'success': 'User stats updated successfully', 'new_stats': updated_stats}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@user_management.route('/users', methods=['GET'])
@admin_role_required
def get_all_users():
    """
    (ADMIN ONLY) Get All Users 
    This endpoint returns all users in the system. Access is restricted to administrators only.
    ---
    tags:
      - User Management
    security:
      - Bearer: []
    consumes:
      - application/json
    produces:
      - application/json
    responses:
      200:
        description: Users fetched successfully.
        schema:
          type: array
          items:
            $ref: '#/definitions/User'
      500:
        description: Internal server error.
        examples:
          application/json: {"error": "An unexpected error occurred"}
    definitions:
      User:
        type: object
        properties:
          user_id:
            type: integer
            description: The user's ID.
          username:
            type: string
            description: The user's username.
          email:
            type: string
            description: The user's email.
    """
    session = Session()
    try:
        users = session.query(User).all()
        users_data = [
            {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
            }
            for user in users
        ]
        return jsonify(users_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@user_management.route('/users/<int:user_id>', methods=['GET'])
@admin_role_required
def get_user_by_id(user_id):
    """
    (ADMIN ONLY) Get User By ID
    This endpoint returns the user with the specified ID. Access is restricted to administrators only.
    ---
    tags:
      - User Management
    security:
      - Bearer: []
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: path
        name: user_id
        required: true
        type: integer
        description: The ID of the user to fetch.
    responses:
      200:
        description: User fetched successfully.
        schema:
          type: object
          $ref: '#/definitions/User'
      404:
        description: User not found.
        examples:
          application/json: {"error": "User not found"}
      500:
        description: Internal server error.
        examples:
          application/json: {"error": "An unexpected error occurred"}
    definitions:
      User:
        type: object
        properties:
          user_id:
            type: integer
            description: The user's ID.
          username:
            type: string
            description: The user's username.
          email:
            type: string
            description: The user's email.
    """
    session = Session()
    try:
        user = session.query(User).filter_by(user_id=user_id).first()
        if user:
            user_data = {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
            }
            return jsonify(user_data), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@user_management.route('/users/<int:user_id>', methods=['DELETE'])
@admin_role_required
def delete_user(user_id):
    """
    (ADMIN ONLY) Delete User
    This endpoint deletes the user with the specified ID. Access is restricted to administrators only.
    ---
    tags:
      - User Management
    security:
      - Bearer: []
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: path
        name: user_id
        required: true
        type: integer
        description: The ID of the user to delete.
    responses:
      200:
        description: User deleted successfully.
        examples:
          application/json: {"success": "User deleted successfully"}
      404:
        description: User not found.
        examples:
          application/json: {"error": "User not found"}
      500:
        description: Internal server error.
        examples:
          application/json: {"error": "An unexpected error occurred"}
    """
    session = Session()
    try:
        user = session.query(User).filter_by(user_id=user_id).first()
        if user:
            session.delete(user)
            session.commit()
            return jsonify({'success': 'User deleted successfully'}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@user_management.route('/users/<int:user_id>/items', methods=['GET'])
@user_role_required
def get_user_items(user_id):
    """
    Get User Items
    This endpoint returns the items owned by the user with the specified ID.
    ---
    tags:
      - User Management
    security:
      - Bearer: []
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: path
        name: user_id
        required: true
        type: integer
        description: The ID of the user whose items to fetch.
    responses:
      200:
        description: User items fetched successfully.
        schema:
          type: array
          items:
            $ref: '#/definitions/UserItem'
      500:
        description: Internal server error.
        examples:
          application/json: {"error": "An unexpected error occurred"}
    definitions:
      UserItem:
        type: object
        properties:
          item_id:
            type: integer
            description: The item's ID.
          item_level:
            type: integer
            description: The item's level.
          item_xp:
            type: integer
            description: The item's XP.
          is_equipped:
            type: boolean
            description: Whether the item is equipped.
          prestige_level:
            type: integer
            description: The item's prestige level.
          selected_chroma_id:
            type: integer
            description: The selected chroma ID for the item.
          selected_shader_id:
            type: integer
            description: The selected shader ID for the item.
          favorite:
            type: boolean
            description: Whether the item is a favorite.
    """
    session = Session()
    try:
        user_items = session.query(UserItem).filter_by(user_id=user_id).all()
        items_data = [
            {
                'item_id': item.item_id,
                'item_level': item.item_level,
                'item_xp': item.item_xp,
                'is_equipped': item.is_equipped,
                'prestige_level': item.prestige_level,
                'selected_chroma_id': item.selected_chroma_id,
                'selected_shader_id': item.selected_shader_id,
                'favorite': item.favorite
            }
            for item in user_items
        ]
        return jsonify(items_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@user_management.route('/users/<int:user_id>/stats', methods=['GET'])
@user_role_required
def get_user_stats(user_id):
    """
    Get User Stats
    This endpoint returns the stats of the user with the specified ID.
    ---
    tags:
      - User Management
    security:
      - Bearer: []
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: path
        name: user_id
        required: true
        type: integer
        description: The ID of the user whose stats to fetch.
    responses:
      200:
        description: User stats fetched successfully.
        schema:
          type: object
          properties:
            minigames_completed:
              type: integer
              description: The total number of minigames completed by the user.
            games_won:
              type: integer
              description: The total number of games won by the user.
            rituals_completed:
              type: integer
              description: The number of rituals the user has completed.
          404:
            description: User stats not found.
            examples:
              application/json: {"error": "User stats not found"}
          500:
            description: Internal server error.
            examples:
              application/json: {"error": "An unexpected error occurred"}
    """
    session = Session()
    try:
        user_stats = session.query(Stat).filter_by(user_id=user_id).first()
        if user_stats:
            stats_data = {
                'minigames_completed': user_stats.minigames_completed,
                'games_won': user_stats.games_won,
                'rituals_completed': user_stats.rituals_completed
            }
            return jsonify(stats_data), 200
        else:
            return jsonify({'error': 'User stats not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@user_management.route('/users/<int:user_id>/referrals', methods=['GET'])
@user_role_required
def get_user_referrals(user_id):
    """
    Get User Referrals
    This endpoint returns the referrals made by the user with the specified ID.
    ---
    tags:
      - User Management
    security:
      - Bearer: []
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: path
        name: user_id
        required: true
        type: integer
        description: The ID of the user whose referrals to fetch.
    responses:
      200:
        description: User referrals fetched successfully.
        schema:
          type: array
          items:
            $ref: '#/definitions/Referral'
      500:
        description: Internal server error.
        examples:
          application/json: {"error": "An unexpected error occurred"}
    definitions:
      Referral:
        type: object
        properties:
          referral_id:
            type: integer
            description: The referral's ID.
          referred_user_id:
            type: integer
            description: The ID of the user referred by the referrer.
          games_played:
            type: integer
            description: The number of games played by the referred user.
          reward_granted:
            type: boolean
            description: Whether the reward has been granted for this referral.
          date_referred:
            type: string
            format: date-time
            description: The date the user was referred.
    """
    session = Session()
    try:
        referrals = session.query(Referral).filter_by(referrer_user_id=user_id).all()
        referrals_data = [
            {
                'referral_id': referral.referral_id,
                'referred_user_id': referral.referred_user_id,
                'games_played': referral.games_played,
                'reward_granted': referral.reward_granted,
                'date_referred': referral.date_referred.isoformat()
            }
            for referral in referrals
        ]
        return jsonify(referrals_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@user_management.route('/users/<int:user_id>/xp-boosters', methods=['GET'])
@user_role_required
def get_user_xp_boosters(user_id):
    """
    Get User XP Boosters
    This endpoint returns the XP boosters owned by the user with the specified ID.
    ---
    tags:
      - User Management
    security:
      - Bearer: []
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: path
        name: user_id
        required: true
        type: integer
        description: The ID of the user whose XP boosters to fetch.
    responses:
      200:
        description: User XP boosters fetched successfully.
        schema:
          type: array
          items:
            $ref: '#/definitions/XPBooster'
      500:
        description: Internal server error.
        examples:
          application/json: {"error": "An unexpected error occurred"}
    definitions:
      XPBooster:
        type: object
        properties:
          booster_id:
            type: integer
            description: The booster's ID.
          booster_type_id:
            type: integer
            description: The ID of the booster type.
          booster_effect:
            type: integer
            description: The effect of the booster.
          is_active:
            type: boolean
            description: Whether the booster is active.
          games_applied:
            type: integer
            description: The number of games the booster has been applied to.
    """

    session = Session()
    try:
        xp_boosters = session.query(XPBooster).filter_by(user_id=user_id).all()
        boosters_data = [
            {
                'booster_id': booster.booster_id,
                'booster_type_id': booster.booster_type_id,
                'booster_effect': booster.booster_effect,
                'is_active': booster.is_active,
                'games_applied': booster.games_applied
            }
            for booster in xp_boosters
        ]
        return jsonify(boosters_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()      