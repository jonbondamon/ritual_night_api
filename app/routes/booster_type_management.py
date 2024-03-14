from flask import Blueprint, request, jsonify
from app.routes import admin_role_required
from app.models import Session, BoosterType

booster_type_management = Blueprint('booster_type_management', __name__, url_prefix='/api')

@booster_type_management.route('/booster-types', methods=['GET'])
def get_all_booster_types():
    """
    Get All Booster Types
    This endpoint retrieves all booster types.
    ---
    tags:
      - Booster Type Management
    responses:
      200:
        description: List of booster types.
        schema:
          type: array
          items:
            $ref: '#/definitions/BoosterType'
      500:
        description: Internal server error.
    definitions:
      BoosterType:
        type: object
        properties:
          booster_type_id:
            type: integer
            description: The unique identifier of the booster type.
          booster_name:
            type: string
            description: The name of the booster type.
          description:
            type: string
            description: The description of the booster type.
    """
    session = Session()
    try:
        booster_types = session.query(BoosterType).all()
        booster_types_list = [
            {
                'booster_type_id': booster_type.booster_type_id,
                'booster_name': booster_type.booster_name,
                'description': booster_type.description
            } for booster_type in booster_types
        ]
        return jsonify(booster_types_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@booster_type_management.route('/booster-types/<int:booster_type_id>', methods=['GET'])
def get_booster_type(booster_type_id):
    """
    Get Booster Type
    This endpoint retrieves a specific booster type by ID.
    ---
    tags:
      - Booster Type Management
    parameters:
      - name: booster_type_id
        in: path
        description: ID of the booster type to retrieve.
        required: true
        type: integer
    responses:
      200:
        description: Booster type details.
        schema:
          $ref: '#/definitions/BoosterType'
      404:
        description: Booster type not found.
      500:
        description: Internal server error.
    """
    session = Session()
    try:
        booster_type = session.query(BoosterType).filter_by(booster_type_id=booster_type_id).first()
        if booster_type:
            booster_type_data = {
                'booster_type_id': booster_type.booster_type_id,
                'booster_name': booster_type.booster_name,
                'description': booster_type.description
            }
            return jsonify(booster_type_data), 200
        else:
            return jsonify({'error': 'Booster type not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@booster_type_management.route('/booster-types', methods=['POST'])
@admin_role_required
def create_booster_type():
    """
    Create Booster Type
    This endpoint creates a new booster type.
    ---
    tags:
      - Booster Type Management
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        description: Booster type details.
        required: true
        schema:
          type: object
          properties:
            booster_name:
              type: string
              description: The name of the booster type.
            description:
              type: string
              description: The description of the booster type.
    responses:
      201:
        description: Booster type created successfully.
      400:
        description: Missing required fields.
      500:
        description: Internal server error.
    """
    session = Session()
    try:
        data = request.get_json()
        booster_name = data.get('booster_name')
        description = data.get('description')
        if not booster_name or not description:
            return jsonify({'error': 'Missing required fields'}), 400
        new_booster_type = BoosterType(booster_name=booster_name, description=description)
        session.add(new_booster_type)
        session.commit()
        return jsonify({'success': 'Booster type created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@booster_type_management.route('/booster-types/<int:booster_type_id>', methods=['PUT'])
@admin_role_required
def update_booster_type(booster_type_id):
    """
    Update Booster Type
    This endpoint updates a booster type.
    ---
    tags:
      - Booster Type Management
    security:
      - Bearer: []
    parameters:
      - name: booster_type_id
        in: path
        description: ID of the booster type to update.
        required: true
        type: integer
      - name: body
        in: body
        description: Updated booster type details.
        required: true
        schema:
          type: object
          properties:
            booster_name:
              type: string
              description: The updated name of the booster type.
            description:
              type: string
              description: The updated description of the booster type.
    responses:
      200:
        description: Booster type updated successfully.
      400:
        description: Missing required fields.
      404:
        description: Booster type not found.
      500:
        description: Internal server error.
    """
    session = Session()
    try:
        booster_type = session.query(BoosterType).filter_by(booster_type_id=booster_type_id).first()
        if not booster_type:
            return jsonify({'error': 'Booster type not found'}), 404
        data = request.get_json()
        booster_name = data.get('booster_name')
        description = data.get('description')
        if not booster_name or not description:
            return jsonify({'error': 'Missing required fields'}), 400
        booster_type.booster_name = booster_name
        booster_type.description = description
        session.commit()
        return jsonify({'success': 'Booster type updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@booster_type_management.route('/booster-types/<int:booster_type_id>', methods=['DELETE'])
@admin_role_required
def delete_booster_type(booster_type_id):
    """
    Delete Booster Type
    This endpoint deletes a booster type.
    ---
    tags:
      - Booster Type Management
    security:
      - Bearer: []
    parameters:
      - name: booster_type_id
        in: path
        description: ID of the booster type to delete.
        required: true
        type: integer
    responses:
      200:
        description: Booster type deleted successfully.
      404:
        description: Booster type not found.
      500:
        description: Internal server error.
    """
    session = Session()
    try:
        booster_type = session.query(BoosterType).filter_by(booster_type_id=booster_type_id).first()
        if not booster_type:
            return jsonify({'error': 'Booster type not found'}), 404
        session.delete(booster_type)
        session.commit()
        return jsonify({'success': 'Booster type deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()