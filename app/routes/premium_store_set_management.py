from flask import Blueprint, request, jsonify
from app.routes import admin_role_required
from app.models import Session, PremiumStoreSet, SetItemAssociation, Item
premium_store_set_management = Blueprint('premium_store_set_management', __name__)
@premium_store_set_management.route('/api/premium-store-sets', methods=['GET'])
def get_all_premium_store_set_management():
    """
    Get All Premium Store Sets
    This endpoint retrieves all premium store sets.
    ---
    tags:
      - Premium Store Set Management
    responses:
      200:
        description: List of all premium store sets.
        examples:
          application/json: [{"set_id": 1, "set_name": "Premium Set 1"}, {"set_id": 2, "set_name": "Premium Set 2"}]
      500:
        description: Internal server error, if any exception occurs.
        examples:
          application/json: {"error": "Failed to fetch premium store sets", "details": "<exception details>"}
    """
    session = Session()
    try:
        premium_store_set_management = session.query(PremiumStoreSet).all()
        sets_list = [{"set_id": set.set_id, "set_name": set.set_name} for set in premium_store_set_management]
        return jsonify(sets_list), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch premium store sets', 'details': str(e)}), 500
    finally:
        session.close()
@premium_store_set_management.route('/api/premium-store-sets/<int:set_id>', methods=['GET'])
def get_premium_store_set(set_id):
    """
    Get Premium Store Set
    This endpoint retrieves a specific premium store set by ID.
    ---
    tags:
      - Premium Store Set Management
    parameters:
      - in: path
        name: set_id
        description: ID of the premium store set to retrieve
        required: true
        type: integer
    responses:
      200:
        description: Premium store set details.
        examples:
          application/json: {"set_id": 1, "set_name": "Premium Set 1", "items": [{"item_id": 1, "item_name": "Item 1"}, {"item_id": 2, "item_name": "Item 2"}]}
      404:
        description: Premium store set not found.
        examples:
          application/json: {"error": "Premium store set not found"}
      500:
        description: Internal server error, if any exception occurs.
        examples:
          application/json: {"error": "Failed to fetch premium store set", "details": "<exception details>"}
    """
    session = Session()
    try:
        premium_store_set = session.query(PremiumStoreSet).filter_by(set_id=set_id).first()
        if not premium_store_set:
            return jsonify({'error': 'Premium store set not found'}), 404
        items = [{"item_id": item.item_id, "item_name": item.item.item_name} for item in premium_store_set.items]
        set_details = {"set_id": premium_store_set.set_id, "set_name": premium_store_set.set_name, "items": items}
        return jsonify(set_details), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch premium store set', 'details': str(e)}), 500
    finally:
        session.close()
@premium_store_set_management.route('/api/premium-store-sets', methods=['POST'])
@admin_role_required
def create_premium_store_set():
    """
    Create Premium Store Set
    This endpoint creates a new premium store set.
    ---
    tags:
      - Premium Store Set Management
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        description: Premium store set details
        required: true
        schema:
          type: object
          properties:
            set_name:
              type: string
              description: Name of the premium store set
            item_ids:
              type: array
              items:
                type: integer
              description: List of item IDs to include in the set
    responses:
      201:
        description: Premium store set created successfully.
        examples:
          application/json: {"success": "Premium store set created successfully", "set_id": 1}
      400:
        description: Bad request, if required fields are missing or invalid.
        examples:
          application/json: {"error": "Missing required fields"}
      500:
        description: Internal server error, if any exception occurs.
        examples:
          application/json: {"error": "Failed to create premium store set", "details": "<exception details>"}
    """
    session = Session()
    try:
        data = request.get_json()
        set_name = data.get('set_name')
        item_ids = data.get('item_ids')
        if not set_name or not item_ids:
            return jsonify({'error': 'Missing required fields'}), 400
        new_set = PremiumStoreSet(set_name=set_name)
        session.add(new_set)
        session.commit()
        for item_id in item_ids:
            item = session.query(Item).filter_by(item_id=item_id).first()
            if item:
                association = SetItemAssociation(set_id=new_set.set_id, item_id=item_id)
                session.add(association)
        session.commit()
        return jsonify({'success': 'Premium store set created successfully', 'set_id': new_set.set_id}), 201
    except Exception as e:
        return jsonify({'error': 'Failed to create premium store set', 'details': str(e)}), 500
    finally:
        session.close()
@premium_store_set_management.route('/api/premium-store-sets/<int:set_id>', methods=['PUT'])
@admin_role_required
def update_premium_store_set(set_id):
    """
    Update Premium Store Set
    This endpoint updates a premium store set.
    ---
    tags:
      - Premium Store Set Management
    security:
      - Bearer: []
    parameters:
      - in: path
        name: set_id
        description: ID of the premium store set to update
        required: true
        type: integer
      - in: body
        name: body
        description: Updated premium store set details
        required: true
        schema:
          type: object
          properties:
            set_name:
              type: string
              description: Updated name of the premium store set
            item_ids:
              type: array
              items:
                type: integer
              description: Updated list of item IDs to include in the set
    responses:
      200:
        description: Premium store set updated successfully.
        examples:
          application/json: {"success": "Premium store set updated successfully"}
      400:
        description: Bad request, if required fields are missing or invalid.
        examples:
          application/json: {"error": "Missing required fields"}
      404:
        description: Premium store set not found.
        examples:
          application/json: {"error": "Premium store set not found"}
      500:
        description: Internal server error, if any exception occurs.
        examples:
          application/json: {"error": "Failed to update premium store set", "details": "<exception details>"}
    """
    session = Session()
    try:
        premium_store_set = session.query(PremiumStoreSet).filter_by(set_id=set_id).first()
        if not premium_store_set:
            return jsonify({'error': 'Premium store set not found'}), 404
        data = request.get_json()
        set_name = data.get('set_name')
        item_ids = data.get('item_ids')
        if not set_name or not item_ids:
            return jsonify({'error': 'Missing required fields'}), 400
        premium_store_set.set_name = set_name
        session.query(SetItemAssociation).filter_by(set_id=set_id).delete()
        for item_id in item_ids:
            item = session.query(Item).filter_by(item_id=item_id).first()
            if item:
                association = SetItemAssociation(set_id=set_id, item_id=item_id)
                session.add(association)
        session.commit()
        return jsonify({'success': 'Premium store set updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to update premium store set', 'details': str(e)}), 500
    finally:
        session.close()
@premium_store_set_management.route('/api/premium-store-sets/<int:set_id>', methods=['DELETE'])
@admin_role_required
def delete_premium_store_set(set_id):
    """
    Delete Premium Store Set
    This endpoint deletes a premium store set.
    ---
    tags:
      - Premium Store Set Management
    security:
      - Bearer: []
    parameters:
      - in: path
        name: set_id
        description: ID of the premium store set to delete
        required: true
        type: integer
    responses:
      200:
        description: Premium store set deleted successfully.
        examples:
          application/json: {"success": "Premium store set deleted successfully"}
      404:
        description: Premium store set not found.
        examples:
          application/json: {"error": "Premium store set not found"}
      500:
        description: Internal server error, if any exception occurs.
        examples:
          application/json: {"error": "Failed to delete premium store set", "details": "<exception details>"}
    """
    session = Session()
    try:
        premium_store_set = session.query(PremiumStoreSet).filter_by(set_id=set_id).first()
        if not premium_store_set:
            return jsonify({'error': 'Premium store set not found'}), 404
        session.delete(premium_store_set)
        session.commit()
        return jsonify({'success': 'Premium store set deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to delete premium store set', 'details': str(e)}), 500
    finally:
        session.close()