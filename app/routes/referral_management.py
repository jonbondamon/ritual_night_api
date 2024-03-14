from flask import Blueprint, request, jsonify
from app.routes import user_role_required
from app.models import Session, Referral, User
from datetime import date

referral_management = Blueprint('referral_management', __name__, url_prefix='/api')

@referral_management.route('/referrals', methods=['GET'])
@user_role_required
def get_all_referrals():
    """
    Get All Referrals
    This endpoint retrieves all referrals.
    ---
    tags:
      - Referral Management
    security:
      - Bearer: []
    responses:
      200:
        description: List of all referrals.
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
            description: The unique identifier of the referral.
          referrer_user_id:
            type: integer
            description: The user ID of the referrer.
          referred_user_id:
            type: integer
            description: The user ID of the referred user.
          games_played:
            type: integer
            description: The number of games played by the referred user.
          reward_granted:
            type: boolean
            description: Indicates if the reward has been granted to the referrer.
          date_referred:
            type: string
            format: date
            description: The date when the referral was made.
    """
    session = Session()
    try:
        referrals = session.query(Referral).all()
        referrals_list = [
            {
                'referral_id': referral.referral_id,
                'referrer_user_id': referral.referrer_user_id,
                'referred_user_id': referral.referred_user_id,
                'games_played': referral.games_played,
                'reward_granted': referral.reward_granted,
                'date_referred': referral.date_referred.isoformat()
            } for referral in referrals
        ]
        return jsonify(referrals_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@referral_management.route('/referrals/<int:referral_id>', methods=['GET'])
@user_role_required
def get_referral(referral_id):
    """
    Get Referral
    This endpoint retrieves a specific referral by ID.
    ---
    tags:
      - Referral Management
    security:
      - Bearer: []
    parameters:
      - in: path
        name: referral_id
        required: true
        type: integer
        description: The ID of the referral to retrieve.
    responses:
      200:
        description: The requested referral.
        schema:
          $ref: '#/definitions/Referral'
      404:
        description: Referral not found.
        examples:
          application/json: {"error": "Referral not found"}
      500:
        description: Internal server error.
        examples:
          application/json: {"error": "An unexpected error occurred"}
    """
    session = Session()
    try:
        referral = session.query(Referral).filter_by(referral_id=referral_id).first()
        if referral:
            referral_data = {
                'referral_id': referral.referral_id,
                'referrer_user_id': referral.referrer_user_id,
                'referred_user_id': referral.referred_user_id,
                'games_played': referral.games_played,
                'reward_granted': referral.reward_granted,
                'date_referred': referral.date_referred.isoformat()
            }
            return jsonify(referral_data), 200
        else:
            return jsonify({'error': 'Referral not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@referral_management.route('/referrals', methods=['POST'])
@user_role_required
def create_referral():
    """
    Create Referral
    This endpoint creates a new referral.
    ---
    tags:
      - Referral Management
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - referrer_user_id
            - referred_user_id
          properties:
            referrer_user_id:
              type: integer
              description: The user ID of the referrer.
            referred_user_id:
              type: integer
              description: The user ID of the referred user.
    responses:
      201:
        description: Referral created successfully.
        schema:
          $ref: '#/definitions/Referral'
      400:
        description: Bad request, missing required fields.
        examples:
          application/json: {"error": "Missing required fields"}
      500:
        description: Internal server error.
        examples:
          application/json: {"error": "An unexpected error occurred"}
    """
    session = Session()
    try:
        data = request.get_json()
        referrer_user_id = data.get('referrer_user_id')
        referred_user_id = data.get('referred_user_id')
        if not referrer_user_id or not referred_user_id:
            return jsonify({'error': 'Missing required fields'}), 400
        referrer_user = session.query(User).filter_by(user_id=referrer_user_id).first()
        referred_user = session.query(User).filter_by(user_id=referred_user_id).first()
        if not referrer_user or not referred_user:
            return jsonify({'error': 'Invalid referrer or referred user'}), 400
        new_referral = Referral(
            referrer_user_id=referrer_user_id,
            referred_user_id=referred_user_id,
            date_referred=date.today()
        )
        session.add(new_referral)
        session.commit()
        referral_data = {
            'referral_id': new_referral.referral_id,
            'referrer_user_id': new_referral.referrer_user_id,
            'referred_user_id': new_referral.referred_user_id,
            'games_played': new_referral.games_played,
            'reward_granted': new_referral.reward_granted,
            'date_referred': new_referral.date_referred.isoformat()
        }
        return jsonify(referral_data), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@referral_management.route('/referrals/<int:referral_id>', methods=['PUT'])
@user_role_required
def update_referral(referral_id):
    """
    Update Referral
    This endpoint updates a specific referral by ID.
    ---
    tags:
      - Referral Management
    security:
      - Bearer: []
    parameters:
      - in: path
        name: referral_id
        required: true
        type: integer
        description: The ID of the referral to update.
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            games_played:
              type: integer
              description: The updated number of games played by the referred user.
            reward_granted:
              type: boolean
              description: The updated reward granted status.
    responses:
      200:
        description: Referral updated successfully.
        schema:
          $ref: '#/definitions/Referral'
      404:
        description: Referral not found.
        examples:
          application/json: {"error": "Referral not found"}
      500:
        description: Internal server error.
        examples:
          application/json: {"error": "An unexpected error occurred"}
    """
    session = Session()
    try:
        referral = session.query(Referral).filter_by(referral_id=referral_id).first()
        if referral:
            data = request.get_json()
            games_played = data.get('games_played')
            reward_granted = data.get('reward_granted')
            if games_played is not None:
                referral.games_played = games_played
            if reward_granted is not None:
                referral.reward_granted = reward_granted
            session.commit()
            referral_data = {
                'referral_id': referral.referral_id,
                'referrer_user_id': referral.referrer_user_id,
                'referred_user_id': referral.referred_user_id,
                'games_played': referral.games_played,
                'reward_granted': referral.reward_granted,
                'date_referred': referral.date_referred.isoformat()
            }
            return jsonify(referral_data), 200
        else:
            return jsonify({'error': 'Referral not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@referral_management.route('/referrals/<int:referral_id>', methods=['DELETE'])
@user_role_required
def delete_referral(referral_id):
    """
    Delete Referral
    This endpoint deletes a specific referral by ID.
    ---
    tags:
      - Referral Management
    security:
      - Bearer: []
    parameters:
      - in: path
        name: referral_id
        required: true
        type: integer
        description: The ID of the referral to delete.
    responses:
      200:
        description: Referral deleted successfully.
        examples:
          application/json: {"success": "Referral deleted successfully"}
      404:
        description: Referral not found.
        examples:
          application/json: {"error": "Referral not found"}
      500:
        description: Internal server error.
        examples:
          application/json: {"error": "An unexpected error occurred"}
    """
    session = Session()
    try:
        referral = session.query(Referral).filter_by(referral_id=referral_id).first()
        if referral:
            session.delete(referral)
            session.commit()
            return jsonify({'success': 'Referral deleted successfully'}), 200
        else:
            return jsonify({'error': 'Referral not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()