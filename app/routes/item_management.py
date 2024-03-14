from flask import Blueprint, request, jsonify
from app.routes import admin_role_required, user_role_required
from app.models import Session, Item

item_management = Blueprint('item_management', __name__, url_prefix='/api')

@item_management.route('/items', methods=['GET'])
@admin_role_required
def get_all_items():
    """
    Get All Items
    This endpoint retrieves all items.
    ---
    tags:
      - Item Management
    responses:
      200:
        description: List of items.
        schema:
          type: array
          items:
            $ref: '#/definitions/Item'
      500:
        description: Internal server error.
    definitions:
      Item:
        type: object
        properties:
          item_id:
            type: integer
          item_name:
            type: string
          item_type_id:
            type: integer
          silver_cost:
            type: integer
          gold_cost:
            type: integer
          rarity_id:
            type: integer
          unity_name:
            type: string
          is_general_store_item:
            type: boolean
    """
    session = Session()
    try:
        items = session.query(Item).all()
        items_list = [
            {
                'item_id': item.item_id,
                'item_name': item.item_name,
                'item_type_id': item.item_type_id,
                'silver_cost': item.silver_cost,
                'gold_cost': item.gold_cost,
                'rarity_id': item.rarity_id,
                'unity_name': item.unity_name,
                'is_general_store_item': item.is_general_store_item
            } for item in items
        ]
        return jsonify(items_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@item_management.route('/items/<int:item_id>', methods=['GET'])
@user_role_required
def get_item(item_id):
    """
    Get Item
    This endpoint retrieves a specific item by ID.
    ---
    tags:
      - Item Management
    parameters:
      - name: item_id
        in: path
        description: ID of the item to retrieve.
        required: true
        type: integer
    responses:
      200:
        description: Item details.
        schema:
          $ref: '#/definitions/Item'
      404:
        description: Item not found.
      500:
        description: Internal server error.
    definitions:
      Item:
        type: object
        properties:
          item_id:
            type: integer
          item_name:
            type: string
          item_type_id:
            type: integer
          silver_cost:
            type: integer
          gold_cost:
            type: integer
          rarity_id:
            type: integer
          unity_name:
            type: string
          is_general_store_item:
            type: boolean
    """
    session = Session()
    try:
        item = session.query(Item).filter_by(item_id=item_id).first()
        if item:
            item_data = {
                'item_id': item.item_id,
                'item_name': item.item_name,
                'item_type_id': item.item_type_id,
                'silver_cost': item.silver_cost,
                'gold_cost': item.gold_cost,
                'rarity_id': item.rarity_id,
                'unity_name': item.unity_name,
                'is_general_store_item': item.is_general_store_item
            }
            return jsonify(item_data), 200
        else:
            return jsonify({'error': 'Item not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@item_management.route('/items', methods=['POST'])
@admin_role_required
def create_item():
    """
    (ADMIN ONLY) Create Item
    This endpoint creates a new item.
    ---
    tags:
      - Item Management
    parameters:
      - name: body
        in: body
        description: Item details.
        required: true
        schema:
          $ref: '#/definitions/ItemCreate'
    responses:
      201:
        description: Item created successfully.
      400:
        description: Invalid request data.
      500:
        description: Internal server error.
    definitions:
      ItemCreate:
        type: object
        required:
          - item_name
          - item_type_id
          - rarity_id
          - unity_name
        properties:
          item_name:
            type: string
          item_type_id:
            type: integer
          silver_cost:
            type: integer
          gold_cost:
            type: integer
          rarity_id:
            type: integer
          unity_name:
            type: string
          is_general_store_item:
            type: boolean
    """
    session = Session()
    try:
        data = request.get_json()
        item_name = data.get('item_name')
        item_type_id = data.get('item_type_id')
        silver_cost = data.get('silver_cost')
        gold_cost = data.get('gold_cost')
        rarity_id = data.get('rarity_id')
        unity_name = data.get('unity_name')
        is_general_store_item = data.get('is_general_store_item', False)

        if not item_name or not item_type_id or not rarity_id or not unity_name:
            return jsonify({'error': 'Missing required fields'}), 400

        new_item = Item(
            item_name=item_name,
            item_type_id=item_type_id,
            silver_cost=silver_cost,
            gold_cost=gold_cost,
            rarity_id=rarity_id,
            unity_name=unity_name,
            is_general_store_item=is_general_store_item
        )
        session.add(new_item)
        session.commit()
        return jsonify({'success': 'Item created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@item_management.route('/items/<int:item_id>', methods=['PUT'])
@admin_role_required
def update_item(item_id):
    """
    (ADMIN ONLY) Update Item
    This endpoint updates an existing item.
    ---
    tags:
      - Item Management
    parameters:
      - name: item_id
        in: path
        description: ID of the item to update.
        required: true
        type: integer
      - name: body
        in: body
        description: Updated item details.
        required: true
        schema:
          $ref: '#/definitions/ItemUpdate'
    responses:
      200:
        description: Item updated successfully.
      400:
        description: Invalid request data.
      404:
        description: Item not found.
      500:
        description: Internal server error.
    definitions:
      ItemUpdate:
        type: object
        properties:
          item_name:
            type: string
          item_type_id:
            type: integer
          silver_cost:
            type: integer
          gold_cost:
            type: integer
          rarity_id:
            type: integer
          unity_name:
            type: string
          is_general_store_item:
            type: boolean
    """
    session = Session()
    try:
        item = session.query(Item).filter_by(item_id=item_id).first()
        if not item:
            return jsonify({'error': 'Item not found'}), 404

        data = request.get_json()
        item_name = data.get('item_name')
        item_type_id = data.get('item_type_id')
        silver_cost = data.get('silver_cost')
        gold_cost = data.get('gold_cost')
        rarity_id = data.get('rarity_id')
        unity_name = data.get('unity_name')
        is_general_store_item = data.get('is_general_store_item')

        if item_name:
            item.item_name = item_name
        if item_type_id:
            item.item_type_id = item_type_id
        if silver_cost is not None:
            item.silver_cost = silver_cost
        if gold_cost is not None:
            item.gold_cost = gold_cost
        if rarity_id:
            item.rarity_id = rarity_id
        if unity_name:
            item.unity_name = unity_name
        if is_general_store_item is not None:
            item.is_general_store_item = is_general_store_item

        session.commit()
        return jsonify({'success': 'Item updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@item_management.route('/items/<int:item_id>', methods=['DELETE'])
@admin_role_required
def delete_item(item_id):
    """
    (ADMIN ONLY) Delete Item
    This endpoint deletes an item.
    ---
    tags:
      - Item Management
    parameters:
      - name: item_id
        in: path
        description: ID of the item to delete.
        required: true
        type: integer
    responses:
      200:
        description: Item deleted successfully.
      404:
        description: Item not found.
      500:
        description: Internal server error.
    """
    session = Session()
    try:
        item = session.query(Item).filter_by(item_id=item_id).first()
        if not item:
            return jsonify({'error': 'Item not found'}), 404

        session.delete(item)
        session.commit()
        return jsonify({'success': 'Item deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()