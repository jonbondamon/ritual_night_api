from flask import Blueprint, request, jsonify
from app.models import Session, RarityType
from app.routes import admin_role_required

rarity_type_management = Blueprint('rarity_type_management', __name__, url_prefix='/api')

@rarity_type_management.route('/rarity-types', methods=['GET'])
def get_all_rarity_types():
    """
    Get All Rarity Types
    This endpoint retrieves all rarity types.
    ---
    tags:
      - Rarity Type Management
    responses:
      200:
        description: List of rarity types.
        schema:
          type: array
          items:
            $ref: '#/definitions/RarityType'
      500:
        description: Internal server error.
    definitions:
      RarityType:
        type: object
        properties:
          rarity_id:
            type: integer
            description: The unique identifier of the rarity type.
          rarity_name:
            type: string
            description: The name of the rarity type.
    """
    session = Session()
    try:
        rarity_types = session.query(RarityType).all()
        rarity_types_list = [
            {
                'rarity_id': rarity_type.rarity_id,
                'rarity_name': rarity_type.rarity_name
            } for rarity_type in rarity_types
        ]
        return jsonify(rarity_types_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@rarity_type_management.route('/rarity-types/<int:rarity_id>', methods=['GET'])
def get_rarity_type(rarity_id):
    """
    Get Rarity Type
    This endpoint retrieves a specific rarity type by ID.
    ---
    tags:
      - Rarity Type Management
    parameters:
      - name: rarity_id
        in: path
        description: ID of the rarity type to retrieve.
        required: true
        type: integer
    responses:
      200:
        description: Rarity type details.
        schema:
          $ref: '#/definitions/RarityType'
      404:
        description: Rarity type not found.
      500:
        description: Internal server error.
    definitions:
      RarityType:
        type: object
        properties:
          rarity_id:
            type: integer
            description: The unique identifier of the rarity type.
          rarity_name:
            type: string
            description: The name of the rarity type.
    """
    session = Session()
    try:
        rarity_type = session.query(RarityType).filter_by(rarity_id=rarity_id).first()
        if rarity_type:
            rarity_type_data = {
                'rarity_id': rarity_type.rarity_id,
                'rarity_name': rarity_type.rarity_name
            }
            return jsonify(rarity_type_data), 200
        else:
            return jsonify({'error': 'Rarity type not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@rarity_type_management.route('/rarity-types', methods=['POST'])
@admin_role_required
def create_rarity_type():
    """
    Create Rarity Type
    This endpoint creates a new rarity type.
    ---
    tags:
      - Rarity Type Management
    parameters:
      - name: body
        in: body
        description: Rarity type details.
        required: true
        schema:
          $ref: '#/definitions/RarityTypeCreate'
    responses:
      201:
        description: Rarity type created successfully.
      400:
        description: Invalid request payload.
      500:
        description: Internal server error.
    definitions:
      RarityTypeCreate:
        type: object
        required:
          - rarity_name
        properties:
          rarity_name:
            type: string
            description: The name of the rarity type.
    """
    session = Session()
    try:
        data = request.get_json()
        rarity_name = data.get('rarity_name')
        if not rarity_name:
            return jsonify({'error': 'Rarity name is required'}), 400
        new_rarity_type = RarityType(rarity_name=rarity_name)
        session.add(new_rarity_type)
        session.commit()
        return jsonify({'message': 'Rarity type created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@rarity_type_management.route('/rarity-types/<int:rarity_id>', methods=['PUT'])
@admin_role_required
def update_rarity_type(rarity_id):
    """
    Update Rarity Type
    This endpoint updates a specific rarity type by ID.
    ---
    tags:
      - Rarity Type Management
    parameters:
      - name: rarity_id
        in: path
        description: ID of the rarity type to update.
        required: true
        type: integer
      - name: body
        in: body
        description: Updated rarity type details.
        required: true
        schema:
          $ref: '#/definitions/RarityTypeUpdate'
    responses:
      200:
        description: Rarity type updated successfully.
      400:
        description: Invalid request payload.
      404:
        description: Rarity type not found.
      500:
        description: Internal server error.
    definitions:
      RarityTypeUpdate:
        type: object
        required:
          - rarity_name
        properties:
          rarity_name:
            type: string
            description: The updated name of the rarity type.
    """
    session = Session()
    try:
        data = request.get_json()
        rarity_name = data.get('rarity_name')
        if not rarity_name:
            return jsonify({'error': 'Rarity name is required'}), 400
        rarity_type = session.query(RarityType).filter_by(rarity_id=rarity_id).first()
        if rarity_type:
            rarity_type.rarity_name = rarity_name
            session.commit()
            return jsonify({'message': 'Rarity type updated successfully'}), 200
        else:
            return jsonify({'error': 'Rarity type not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@rarity_type_management.route('/rarity-types/<int:rarity_id>', methods=['DELETE'])
@admin_role_required
def delete_rarity_type(rarity_id):
    """
    Delete Rarity Type
    This endpoint deletes a specific rarity type by ID.
    ---
    tags:
      - Rarity Type Management
    parameters:
      - name: rarity_id
        in: path
        description: ID of the rarity type to delete.
        required: true
        type: integer
    responses:
      200:
        description: Rarity type deleted successfully.
      404:
        description: Rarity type not found.
      500:
        description: Internal server error.
    """
    session = Session()
    try:
        rarity_type = session.query(RarityType).filter_by(rarity_id=rarity_id).first()
        if rarity_type:
            session.delete(rarity_type)
            session.commit()
            return jsonify({'message': 'Rarity type deleted successfully'}), 200
        else:
            return jsonify({'error': 'Rarity type not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()