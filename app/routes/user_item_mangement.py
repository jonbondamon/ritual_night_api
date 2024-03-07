from app.routes import user_role_required
from flask import Blueprint, request, jsonify
from app.models import Session, User, UserItem

user_item_management = Blueprint('user_item_management', __name__, url_prefix='/api')

@user_item_management.route('/user/item/favorite', methods=['PUT'])
@user_role_required
def update_item_favorite():
    """
    Update Item Status
    This endpoint allows the authenticated user to update the status of an item.
    ---
    tags:
      - User Item Management
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - in: query
        name: item_id
        description: ID of the item to update
        required: true
        type: integer
      - in: query
        name: status
        description: New status for the item (true or false)
        required: true
        type: boolean
    responses:
      200:
        description: Item status updated successfully.
        examples:
          application/json: {"success": "Item status updated successfully"}
      400:
        description: Bad request, if required fields are missing in the query string.
        examples:
          application/json: {"error": "Missing required fields"}
      404:
        description: Item not found, if no item matches the provided item ID.
        examples:
          application/json: {"error": "Item not found"}
      500:
        description: Internal server error, if any exception occurs.
        examples:
          application/json: {"error": "Failed to update item status", "details": "<exception details>"}
    """
    session = Session()
    try:
        user_id = request.user_id  # Get the user ID from the JWT token
        item_id = int(request.args.get('item_id'))  # Get item_id from the query string
        status = request.args.get('status')  # Get status from the query string

        # Validate the presence of required fields
        if not item_id or status is None:
            return jsonify({'error': 'Missing required fields'}), 400

        # Convert status to boolean
        status = status.lower() == 'true'

        # Fetch the item from the database
        item = session.query(UserItem).filter_by(item_id=item_id, user_id=user_id).first()
        if not item:
            return jsonify({'error': 'Item not found'}), 404

        # Update item status
        item.favorite = status
        session.commit()  # Commit changes to the database

        return jsonify({'success': 'Item status updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to update item status', 'details': str(e)}), 500
    finally:
        session.close()

@user_item_management.route('/user/item/equip', methods=['PUT'])
@user_role_required
def equip_item():
    """
    Equip Item
    This endpoint allows the authenticated user to equip an item.
    ---
    tags:
      - User Item Management
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - in: query
        name: item_id
        description: ID of the item to equip
        required: true
        type: integer
    responses:
      200:
        description: Item equipped successfully.
        examples:
          application/json: {"success": "Item equipped successfully"}
      400:
        description: Bad request, if required fields are missing in the query string.
        examples:
          application/json: {"error": "Missing required fields"}
      404:
        description: Item not found, if no item matches the provided item ID.
        examples:
          application/json: {"error": "Item not found"}
      500:
        description: Internal server error, if any exception occurs.
        examples:
          application/json: {"error": "Failed to equip item", "details": "<exception details>"}
    """
    session = Session()
    try:
        user_id = request.user_id  # Get the user ID from the JWT token
        item_id = int(request.args.get('item_id'))  # Get item_id from the query string
        if not item_id:
            return jsonify({'error': 'Missing required fields'}), 400
        # Fetch the user from the database
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        # Fetch the item to be equipped from the user's items
        item_to_equip = next((item for item in user.user_items if item.item_id == item_id), None)
        if not item_to_equip:
            return jsonify({'error': 'Item not found'}), 404
        # Fetch the currently equipped item of the same type
        equipped_item_of_same_type = next((item for item in user.user_items if item.is_equipped and item.item.item_type == item_to_equip.item.item_type), None)
        # If there is an equipped item of the same type, unequip it
        if equipped_item_of_same_type:
            equipped_item_of_same_type.is_equipped = False
        # Equip the new item
        item_to_equip.is_equipped = True
        session.commit()  # Commit changes to the database
        return jsonify({'success': 'Item equipped successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to equip item', 'details': str(e)}), 500
    finally:
        session.close()

@user_item_management.route('/user/item/unequip', methods=['PUT'])
@user_role_required
def unequip_item():
    """
    Unequip Item
    This endpoint allows the authenticated user to unequip an item.
    ---
    tags:
      - User Item Management
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - in: query
        name: item_id
        description: ID of the item to unequip
        required: true
        type: integer
    responses:
      200:
        description: Item unequipped successfully.
        examples:
          application/json: {"success": "Item unequipped successfully"}
      400:
        description: Bad request, if required fields are missing in the query string.
        examples:
          application/json: {"error": "Missing required fields"}
      404:
        description: Item not found, if no item matches the provided item ID.
        examples:
          application/json: {"error": "Item not found"}
      500:
        description: Internal server error, if any exception occurs.
        examples:
          application/json: {"error": "Failed to unequip item", "details": "<exception details>"}
    """
    session = Session()
    try:
        user_id = request.user_id  # Get the user ID from the JWT token
        item_id = int(request.args.get('item_id'))  # Get item_id from the query string
        if not item_id:
            return jsonify({'error': 'Missing required fields'}), 400
        # Fetch the user from the database
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        # Fetch the item to be unequipped from the user's items
        item_to_unequip = next((item for item in user.user_items if item.item_id == item_id), None)
        if not item_to_unequip:
            return jsonify({'error': 'Item not found'}), 404
        # Unequip the item
        item_to_unequip.is_equipped = False
        session.commit()  # Commit changes to the database
        return jsonify({'success': 'Item unequipped successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to unequip item', 'details': str(e)}), 500
    finally:
        session.close()

@user_item_management.route('/user/item/chroma', methods=['PUT'])
@user_role_required
def update_item_chroma():
    """
    Update Item Chroma
    This endpoint allows the authenticated user to update the chroma of an item.
    ---
    tags:
      - User Item Management
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - in: query
        name: item_id
        description: ID of the item to update
        required: true
        type: integer
      - in: query
        name: chroma_id
        description: ID of the chroma to set for the item (if 'c', nullify the selected chroma id)
        required: true
        type: string
    responses:
      200:
        description: Item chroma updated successfully.
        examples:
          application/json: {"success": "Item chroma updated successfully"}
      400:
        description: Bad request, if required fields are missing in the query string.
        examples:
          application/json: {"error": "Missing required fields"}
      404:
        description: Item or chroma not found, if no item or chroma matches the provided IDs.
        examples:
          application/json: {"error": "Item not found"}
      500:
        description: Internal server error, if any exception occurs.
        examples:
          application/json: {"error": "Failed to update item chroma", "details": "<exception details>"}
    """
    session = Session()
    try:
        user_id = request.user_id  # Get the user ID from the JWT token
        item_id = int(request.args.get('item_id'))  # Get item_id from the query string
        chroma_id = request.args.get('chroma_id')  # Get chroma_id from the query string

        if not item_id or not chroma_id:
            return jsonify({'error': 'Missing required fields'}), 400

        # Fetch the user from the database
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Fetch the item to update from the user's items
        item_to_update = next((item for item in user.user_items if item.item_id == item_id), None)
        if not item_to_update:
            return jsonify({'error': 'Item not found'}), 404

        # If chroma_id is 'c', nullify the selected chroma id
        if str(chroma_id) == 'c':
            item_to_update.selected_chroma_id = None
        else:
            chroma_id = int(chroma_id)
            # Check if the chroma exists in the item's chromas
            chroma = next((chroma for chroma in item_to_update.item.chromas if chroma.chroma_id == chroma_id), None)
            if not chroma:
                return jsonify({'error': 'Chroma not found'}), 404

            # Update the item's chroma
            item_to_update.selected_chroma_id = chroma_id

        session.commit()  # Commit changes to the database
        return jsonify({'success': 'Item chroma updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to update item chroma', 'details': str(e)}), 500
    finally:
        session.close()

@user_item_management.route('/user/item/shader', methods=['PUT'])
@user_role_required
def update_item_shader():
    """
    Update Item Shader
    This endpoint allows the authenticated user to update the shader of an item.
    ---
    tags:
      - User Item Management
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - in: query
        name: item_id
        description: ID of the item to update 
        required: true
        type: integer
      - in: query
        name: shader_id
        description: ID of the shader to set for the item (if 'c', nullify the selected shader id)
        required: true
        type: string
    responses:
      200:
        description: Item shader updated successfully.
        examples:
          application/json: {"success": "Item shader updated successfully"}
      400:
        description: Bad request, if required fields are missing in the query string.
        examples:
          application/json: {"error": "Missing required fields"}
      404:
        description: Item or shader not found, if no item or shader matches the provided IDs.
        examples:
          application/json: {"error": "Item not found"}
      500:
        description: Internal server error, if any exception occurs.
        examples:
          application/json: {"error": "Failed to update item shader", "details": "<exception details>"}
    """
    session = Session()
    try:
        user_id = request.user_id  # Get the user ID from the JWT token
        item_id = int(request.args.get('item_id'))  # Get item_id from the query string
        shader_id = request.args.get('shader_id')  # Get shader_id from the query string

        if not item_id or not shader_id:
            return jsonify({'error': 'Missing required fields'}), 400

        # Fetch the user from the database
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Fetch the item to update from the user's items
        item_to_update = next((item for item in user.user_items if item.item_id == item_id), None)
        if not item_to_update:
            return jsonify({'error': 'Item not found'}), 404

        # If shader_id is 'c', nullify the selected shader id
        if str(shader_id) == 'c':
            item_to_update.selected_shader_id = None
        else:
            shader_id = int(shader_id)
            # Check if the shader exists in the item's shaders
            shader = next((shader for shader in item_to_update.item.shaders if shader.shader_id == shader_id), None)
            if not shader:
                return jsonify({'error': 'Shader not found'}), 404

            # Update the item's shader
            item_to_update.selected_shader_id = shader_id
        session.commit()  # Commit changes to the database
        return jsonify({'success': 'Item shader updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to update item shader', 'details': str(e)}), 500
    finally:
        session.close()

@user_item_management.route('/user/item/purchase', methods=['PUT'])
@user_role_required
def purchase_item():
    """
    Purchase Item
    This endpoint allows the authenticated user to purchase an item.
    ---
    tags:
      - User Item Management
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - in: query
        name: item_id
        description: ID of the item to purchase
        required: true
        type: integer
    responses:
      200:
        description: Item purchased successfully.
        examples:
          application/json: {"success": "Item purchased successfully"}
      400:
        description: Bad request, if required fields are missing in the query string.
        examples:
          application/json: {"error": "Missing required fields"}
      404:
        description: Item not found, if no item matches the provided item ID.
        examples:
          application/json: {"error": "Item not found"}
      500:
        description: Internal server error, if any exception occurs.
        examples:
          application/json: {"error": "Failed to purchase item", "details": "<exception details>"}
    """
    session = Session()
    try:
        user_id = request.user_id  # Get the user ID from the JWT token
        item_id = int(request.args.get('item_id'))  # Get item_id from the query string
        if not item_id:
            return jsonify({'error': 'Missing required fields'}), 400
        # Fetch the user from the database
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        # Fetch the item to be purchased from the database
        item_to_purchase = session.query(UserItem).filter_by(item_id=item_id, user_id=user_id).first()
        if not item_to_purchase:
            return jsonify({'error': 'Item not found'}), 404
        # Purchase the item
        item_to_purchase.is_purchased = True
        session.commit()  # Commit changes to the database
        return jsonify({'success': 'Item purchased successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to purchase item', 'details': str(e)}), 500
    finally:
        session.close()