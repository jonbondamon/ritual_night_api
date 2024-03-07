from flask import Blueprint, request, jsonify
from app.routes import user_role_required
from app.models import Session, Item, User, UserItem

store = Blueprint('store', __name__)

@store.route('/store/general/buy', methods=['GET'])
@user_role_required
def buy_general_item():
    """
    Buy Item
    This endpoint allows the authenticated user to buy an item from the store.
    ---
    tags:
      - Store Management
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - in: query
        name: item_id
        description: ID of the item to buy
        required: true
        type: integer
    responses:
      200:
        description: Item bought successfully.
        examples:
          application/json: {"success": "Item bought successfully"}
      400:
        description: Bad request, if required fields are missing in the query string or not enough silver to buy the item or the user already owns the item.
        examples:
          application/json: {"error": "Item id and User id are required", "error": "Not enough silver to buy this item", "error": "You already own this item"}
      404:
        description: Item or User not found, if no item or user matches the provided item ID or user ID.
        examples:
          application/json: {"error": "User or Item not found"}
      500:
        description: Internal server error, if any exception occurs.
        examples:
          application/json: {"error": "Failed to buy item", "details": "<exception details>"}
    """
    session = Session()
    try:
        user_id = request.user_id  # Get the user ID from the JWT token
        item_id = int(request.args.get('item_id'))  # Get item_id from the query string

        # Validate the presence of required fields
        if not item_id or not user_id:
            return jsonify({'error': 'Item id and User id are required'}), 400

        # Fetch the user and item from the database
        user = session.query(User).filter_by(user_id=user_id).first()
        item = session.query(Item).filter_by(item_id=item_id, is_general_store_item=True).first()

        # Check if the user and item exist
        if not user or not item:
            return jsonify({'error': 'User or Item not found'}), 404

        # Check if the user already has the item
        user_item = session.query(UserItem).filter_by(user_id=user_id, item_id=item_id).first()
        if user_item and user_item.is_obtained:
            return jsonify({'error': 'You already own this item'}), 400

        # Check if the user has enough silver to buy the item
        if user.silver < item.silver_cost:
            return jsonify({'error': 'Not enough silver to buy this item'}), 400

        # Deduct the cost of the item from the user's silver
        user.silver -= item.silver_cost

        # Add the item to the user's items
        user_item = UserItem(user_id=user_id, item_id=item_id, is_equipped=False)
        session.add(user_item)

        # Commit the changes to the database
        session.commit()

        return jsonify({'success': 'Item bought successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to buy item', 'details': str(e)}), 500
    finally:
        session.close()

