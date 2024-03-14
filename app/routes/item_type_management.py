from flask import Blueprint, request, jsonify
from app.models import Session, ItemType
from app.routes import admin_role_required

item_type_management = Blueprint('item_type_management', __name__, url_prefix='/api')

@item_type_management.route('/item-types', methods=['GET'])
def get_item_types():
    """
    Get All Item Types
    This endpoint retrieves all item types.
    ---
    tags:
      - Item Type Management
    responses:
      200:
        description: List of item types.
        schema:
          type: array
          items:
            $ref: '#/definitions/ItemType'
      500:
        description: Internal server error.
    definitions:
      ItemType:
        type: object
        properties:
          item_type_id:
            type: integer
            description: The unique identifier of the item type.
          item_type_name:
            type: string
            description: The name of the item type.
    """
    session = Session()
    try:
        item_types = session.query(ItemType).all()
        item_types_list = [
            {
                'item_type_id': item_type.item_type_id,
                'item_type_name': item_type.item_type_name
            } for item_type in item_types
        ]
        return jsonify(item_types_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@item_type_management.route('/item-types/<int:item_type_id>', methods=['GET'])
def get_item_type(item_type_id):
    """
    Get Item Type by ID
    This endpoint retrieves a specific item type by its ID.
    ---
    tags:
      - Item Type Management
    parameters:
      - name: item_type_id
        in: path
        description: ID of the item type to retrieve.
        required: true
        type: integer
    responses:
      200:
        description: Item type details.
        schema:
          $ref: '#/definitions/ItemType'
      404:
        description: Item type not found.
      500:
        description: Internal server error.
    """
    session = Session()
    try:
        item_type = session.query(ItemType).filter_by(item_type_id=item_type_id).first()
        if item_type:
            item_type_data = {
                'item_type_id': item_type.item_type_id,
                'item_type_name': item_type.item_type_name
            }
            return jsonify(item_type_data), 200
        else:
            return jsonify({'error': 'Item type not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@item_type_management.route('/item-types', methods=['POST'])
@admin_role_required
def create_item_type():
    """
    Create Item Type
    This endpoint creates a new item type.
    ---
    tags:
      - Item Type Management
    parameters:
      - name: body
        in: body
        description: Item type details.
        required: true
        schema:
          $ref: '#/definitions/ItemTypeCreate'
    responses:
      201:
        description: Item type created successfully.
      400:
        description: Invalid request payload.
      500:
        description: Internal server error.
    definitions:
      ItemTypeCreate:
        type: object
        required:
          - item_type_name
        properties:
          item_type_name:
            type: string
            description: The name of the item type.
    """
    session = Session()
    try:
        data = request.get_json()
        item_type_name = data.get('item_type_name')
        if not item_type_name:
            return jsonify({'error': 'Missing item type name'}), 400
        new_item_type = ItemType(item_type_name=item_type_name)
        session.add(new_item_type)
        session.commit()
        return jsonify({'message': 'Item type created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@item_type_management.route('/item-types/<int:item_type_id>', methods=['DELETE'])
@admin_role_required
def delete_item_type(item_type_id):
    """
    Delete Item Type
    This endpoint deletes an item type.
    ---
    tags:
      - Item Type Management
    parameters:
      - name: item_type_id
        in: path
        description: ID of the item type to delete.
        required: true
        type: integer
    responses:
      200:
        description: Item type deleted successfully.
      404:
        description: Item type not found.
      500:
        description: Internal server error.
    """
    session = Session()
    try:
        item_type = session.query(ItemType).filter_by(item_type_id=item_type_id).first()
        if item_type:
            session.delete(item_type)
            session.commit()
            return jsonify({'message': 'Item type deleted successfully'}), 200
        else:
            return jsonify({'error': 'Item type not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()