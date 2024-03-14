from flask import Blueprint, request, jsonify
from app.routes import user_role_required
from app.models import Session, Item, User, UserItem, PremiumStoreSet, PremiumStoreSchedule, SetItemAssociation
from sqlalchemy import select
from datetime import datetime

store_management = Blueprint('store', __name__)

@store_management.route('/store/general/buy', methods=['GET'])
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
        if user.silver_amount < item.silver_cost:
            return jsonify({'error': 'Not enough silver to buy this item'}), 400

        # Deduct the cost of the item from the user's silver
        user.silver_amount -= item.silver_cost

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

@store_management.route('/store/premium/buy', methods=['GET'])
@user_role_required
def buy_premium_item():
    """
    Buy Premium Item
    This endpoint allows the authenticated user to buy a premium item from the store if it's currently available.
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
        description: Bad request, if required fields are missing in the query string or not enough gold to buy the item or the user already owns the item.
        examples:
          application/json: {"error": "Item id and User id are required", "error": "Not enough gold to buy this item", "error": "You already own this item"}
      404:
        description: Item or User not found, if no item or user matches the provided item ID or user ID or the item is not available for purchase.
        examples:
          application/json: {"error": "User or Item not found", "error": "Item is not available for purchase or does not exist"}
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
        item = session.query(Item).filter_by(item_id=item_id, is_premium_store_item=True).first()
        # Check if the user and item exist
        if not user or not item:
            return jsonify({'error': 'User or Item not found'}), 404
        # Check if the item is currently available for purchase
        current_time = datetime.utcnow()
        available_item = session.query(Item).join(SetItemAssociation, Item.item_id == SetItemAssociation.item_id)\
                                          .join(PremiumStoreSet, SetItemAssociation.set_id == PremiumStoreSet.set_id)\
                                          .join(PremiumStoreSchedule, PremiumStoreSet.set_id == PremiumStoreSchedule.set_id)\
                                          .filter(Item.item_id == item_id,
                                                  PremiumStoreSchedule.start_date <= current_time,
                                                  PremiumStoreSchedule.end_date >= current_time)\
                                          .first()
        if not available_item:
            return jsonify({'error': 'Item is not available for purchase or does not exist'}), 404
        # Check if the user already has the item
        user_item = session.query(UserItem).filter_by(user_id=user_id, item_id=item_id).first()
        if user_item and user_item.is_obtained:
            return jsonify({'error': 'You already own this item'}), 400
        # Check if the user has enough gold to buy the item
        if user.gold_amount < item.gold_cost:
            return jsonify({'error': 'Not enough gold to buy this item'}), 400
        # Deduct the cost of the item from the user's gold
        user.gold_amount -= item.gold_cost
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

@store_management.route('/store/premium/items', methods=['GET'])
@user_role_required
def get_current_premium_items():
    """
    Get Current Premium Items
    This endpoint provides the list of items currently available in the premium shop.
    ---
    tags:
      - Store Management
    responses:
      200:
        description: List of current premium items.
        examples:
          application/json: [{"item_id": 1, "item_name": "Premium Sword", "gold_cost": 100}]
      500:
        description: Internal server error, if any exception occurs.
        examples:
          application/json: {"error": "Failed to fetch current premium items", "details": "<exception details>"}
    """
    session = Session()
    try:
        # Get current UTC time
        current_time = datetime.utcnow()

        # Fetch current premium sets based on the schedule
        current_sets = session.query(PremiumStoreSet).join(PremiumStoreSchedule).filter(
            PremiumStoreSchedule.start_date <= current_time,
            PremiumStoreSchedule.end_date >= current_time
        ).all()

        # Extract item IDs from the current sets
        item_ids = [item.item_id for set in current_sets for item in set.items]

        # Fetch items details based on item IDs
        items = session.query(Item).filter(Item.item_id.in_(item_ids)).all()

        # Prepare and return the items list
        items_list = [
            {"item_id": item.item_id, "item_name": item.item_name, "gold_cost": item.gold_cost}
            for item in items
        ]

        return jsonify(items_list), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch current premium items', 'details': str(e)}), 500
    finally:
        session.close()

@store_management.route('/store/general/items', methods=['GET'])
@user_role_required
def get_store_items():
    """
    Get Store Items 
    This endpoint returns the items available in the general store that are not owned by the authenticated user.
    ---
    tags:
      - Store Management
    security:
      - Bearer: []
    consumes:
      - application/json
    produces:
      - application/json
    responses:
      200:
        description: Store items fetched successfully.
        schema:
          type: array
          items:
            $ref: '#/definitions/StoreItem'
      500:
        description: Internal server error.
        examples:
          application/json: {"error": "An unexpected error occurred"}
    definitions:
      StoreItem:
        type: object
        properties:
          item_id:
            type: integer
            description: The unique identifier of the item.
          item_name:
            type: string
            description: The name of the item.
          silver_cost:
            type: integer
            description: The cost of the item in silver.
          gold_cost:
            type: integer
            description: The cost of the item in gold.
          unity_name:
            type: string
            description: The name of the item's unity.
          is_general_store_item:
            type: boolean
            description: Indicates if the item is available in the general store.
    """
    session = Session()
    try:
        user_id = request.user_id  # Obtained from the JWT token after @user_role_required decorator

        # Query for items that are in the general store but not owned by the user
        user_owned_item_ids_query = select(UserItem.item_id).filter(UserItem.user_id == user_id)
        
        # Fetch store items not owned by the user
        items = session.query(Item).filter(
            Item.is_general_store_item == True, 
            ~Item.item_id.in_(user_owned_item_ids_query)
        ).all()

        items_list = [
            {
                'item_id': item.item_id,
                'item_name': item.item_name,
                'silver_cost': item.silver_cost,
                'gold_cost': item.gold_cost,
                'unity_name': item.unity_name,
                'is_general_store_item': item.is_general_store_item
            } for item in items
        ]

        return jsonify(items_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()