from flask import Blueprint, request, jsonify
from app.routes import user_role_required
from app.models import Session, XPBooster, User

xp_booster_management = Blueprint('xp_booster_management', __name__, url_prefix='/api')

@xp_booster_management.route('/xp-boosters', methods=['GET'])
@user_role_required
def get_all_xp_boosters():
    """
    Get All XP Boosters
    This endpoint retrieves all XP boosters.
    ---
    tags:
      - XP Booster Management
    security:
      - Bearer: []
    responses:
      200:
        description: List of XP boosters.
        schema:
          type: array
          items:
            $ref: '#/definitions/XPBooster'
      500:
        description: Internal server error.
    definitions:
      XPBooster:
        type: object
        properties:
          booster_id:
            type: integer
          user_id:
            type: integer
          booster_type_id:
            type: integer
          booster_effect:
            type: integer
          is_active:
            type: boolean
          games_applied:
            type: integer
    """
    session = Session()
    try:
        xp_boosters = session.query(XPBooster).all()
        boosters_list = [
            {
                'booster_id': booster.booster_id,
                'user_id': booster.user_id,
                'booster_type_id': booster.booster_type_id,
                'booster_effect': booster.booster_effect,
                'is_active': booster.is_active,
                'games_applied': booster.games_applied
            } for booster in xp_boosters
        ]
        return jsonify(boosters_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@xp_booster_management.route('/xp-boosters/<int:booster_id>', methods=['GET'])
@user_role_required
def get_xp_booster(booster_id):
    """
    Get XP Booster
    This endpoint retrieves a specific XP booster by ID.
    ---
    tags:
      - XP Booster Management
    security:
      - Bearer: []
    parameters:
      - name: booster_id
        in: path
        description: ID of the XP booster to retrieve.
        required: true
        type: integer
    responses:
      200:
        description: XP booster details.
        schema:
          $ref: '#/definitions/XPBooster'
      404:
        description: XP booster not found.
      500:
        description: Internal server error.
    definitions:
      XPBooster:
        type: object
        properties:
          booster_id:
            type: integer
          user_id:
            type: integer
          booster_type_id:
            type: integer
          booster_effect:
            type: integer
          is_active:
            type: boolean
          games_applied:
            type: integer
    """
    session = Session()
    try:
        xp_booster = session.query(XPBooster).filter_by(booster_id=booster_id).first()
        if xp_booster:
            booster_details = {
                'booster_id': xp_booster.booster_id,
                'user_id': xp_booster.user_id,
                'booster_type_id': xp_booster.booster_type_id,
                'booster_effect': xp_booster.booster_effect,
                'is_active': xp_booster.is_active,
                'games_applied': xp_booster.games_applied
            }
            return jsonify(booster_details), 200
        else:
            return jsonify({'error': 'XP booster not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@xp_booster_management.route('/xp-boosters', methods=['POST'])
@user_role_required
def create_xp_booster():
    """
    Create XP Booster
    This endpoint creates a new XP booster.
    ---
    tags:
      - XP Booster Management
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        description: XP booster details.
        required: true
        schema:
          $ref: '#/definitions/XPBoosterCreate'
    responses:
      201:
        description: XP booster created successfully.
      400:
        description: Invalid request data.
      500:
        description: Internal server error.
    definitions:
      XPBoosterCreate:
        type: object
        required:
          - user_id
          - booster_type_id
          - booster_effect
          - games_applied
        properties:
          user_id:
            type: integer
          booster_type_id:
            type: integer
          booster_effect:
            type: integer
          games_applied:
            type: integer
    """
    session = Session()
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        booster_type_id = data.get('booster_type_id')
        booster_effect = data.get('booster_effect')
        games_applied = data.get('games_applied')
        if not user_id or not booster_type_id or not booster_effect or not games_applied:
            return jsonify({'error': 'Invalid request data'}), 400
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        xp_booster = XPBooster(
            user_id=user_id,
            booster_type_id=booster_type_id,
            booster_effect=booster_effect,
            games_applied=games_applied
        )
        session.add(xp_booster)
        session.commit()
        return jsonify({'success': 'XP booster created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@xp_booster_management.route('/xp-boosters/<int:booster_id>', methods=['PUT'])
@user_role_required
def update_xp_booster(booster_id):
    """
    Update XP Booster
    This endpoint updates an existing XP booster.
    ---
    tags:
      - XP Booster Management
    security:
      - Bearer: []
    parameters:
      - name: booster_id
        in: path
        description: ID of the XP booster to update.
        required: true
        type: integer
      - name: body
        in: body
        description: Updated XP booster details.
        required: true
        schema:
          $ref: '#/definitions/XPBoosterUpdate'
    responses:
      200:
        description: XP booster updated successfully.
      400:
        description: Invalid request data.
      404:
        description: XP booster not found.
      500:
        description: Internal server error.
    definitions:
      XPBoosterUpdate:
        type: object
        properties:
          booster_type_id:
            type: integer
          booster_effect:
            type: integer
          is_active:
            type: boolean
          games_applied:
            type: integer
    """
    session = Session()
    try:
        data = request.get_json()
        xp_booster = session.query(XPBooster).filter_by(booster_id=booster_id).first()
        if not xp_booster:
            return jsonify({'error': 'XP booster not found'}), 404
        if 'booster_type_id' in data:
            xp_booster.booster_type_id = data['booster_type_id']
        if 'booster_effect' in data:
            xp_booster.booster_effect = data['booster_effect']
        if 'is_active' in data:
            xp_booster.is_active = data['is_active']
        if 'games_applied' in data:
            xp_booster.games_applied = data['games_applied']
        session.commit()
        return jsonify({'success': 'XP booster updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@xp_booster_management.route('/xp-boosters/<int:booster_id>', methods=['DELETE'])
@user_role_required
def delete_xp_booster(booster_id):
    """
    Delete XP Booster
    This endpoint deletes an XP booster.
    ---
    tags:
      - XP Booster Management
    security:
      - Bearer: []
    parameters:
      - name: booster_id
        in: path
        description: ID of the XP booster to delete.
        required: true
        type: integer
    responses:
      200:
        description: XP booster deleted successfully.
      404:
        description: XP booster not found.
      500:
        description: Internal server error.
    """
    session = Session()
    try:
        xp_booster = session.query(XPBooster).filter_by(booster_id=booster_id).first()
        if not xp_booster:
            return jsonify({'error': 'XP booster not found'}), 404
        session.delete(xp_booster)
        session.commit()
        return jsonify({'success': 'XP booster deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()