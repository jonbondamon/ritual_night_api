from flask import Blueprint, request, jsonify
from app.routes import admin_role_required
from app.models import Session, ItemBundle, BundleItemAssociation, Item
item_bundle_management = Blueprint('item_bundle_management', __name__, url_prefix='/api')
@item_bundle_management.route('/item-bundles', methods=['GET'])
def get_all_item_bundles():
    """
    Get All Item Bundles
    This endpoint retrieves all item bundles.
    ---
    tags:
      - Item Bundle Management
    responses:
      200:
        description: List of item bundles.
        schema:
          type: array
          items:
            $ref: '#/definitions/ItemBundle'
      500:
        description: Internal server error.
    definitions:
      ItemBundle:
        type: object
        properties:
          bundle_id:
            type: integer
          bundle_name:
            type: string
          description:
            type: string
          silver_price:
            type: integer
          gold_price:
            type: integer
    """
    session = Session()
    try:
        item_bundles = session.query(ItemBundle).all()
        bundles_list = [
            {
                'bundle_id': bundle.bundle_id,
                'bundle_name': bundle.bundle_name,
                'description': bundle.description,
                'silver_price': bundle.silver_price,
                'gold_price': bundle.gold_price
            } for bundle in item_bundles
        ]
        return jsonify(bundles_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()
@item_bundle_management.route('/item-bundles/<int:bundle_id>', methods=['GET'])
def get_item_bundle(bundle_id):
    """
    Get Item Bundle
    This endpoint retrieves a specific item bundle by ID.
    ---
    tags:
      - Item Bundle Management
    parameters:
      - name: bundle_id
        in: path
        description: ID of the item bundle.
        required: true
        type: integer
    responses:
      200:
        description: Item bundle details.
        schema:
          $ref: '#/definitions/ItemBundleDetails'
      404:
        description: Item bundle not found.
      500:
        description: Internal server error.
    definitions:
      ItemBundleDetails:
        type: object
        properties:
          bundle_id:
            type: integer
          bundle_name:
            type: string
          description:
            type: string
          silver_price:
            type: integer
          gold_price:
            type: integer
          items:
            type: array
            items:
              $ref: '#/definitions/Item'
      Item:
        type: object
        properties:
          item_id:
            type: integer
          item_name:
            type: string
    """
    session = Session()
    try:
        item_bundle = session.query(ItemBundle).filter_by(bundle_id=bundle_id).first()
        if not item_bundle:
            return jsonify({'error': 'Item bundle not found'}), 404
        bundle_items = session.query(Item).join(BundleItemAssociation).filter_by(bundle_id=bundle_id).all()
        bundle_details = {
            'bundle_id': item_bundle.bundle_id,
            'bundle_name': item_bundle.bundle_name,
            'description': item_bundle.description,
            'silver_price': item_bundle.silver_price,
            'gold_price': item_bundle.gold_price,
            'items': [{'item_id': item.item_id, 'item_name': item.item_name} for item in bundle_items]
        }
        return jsonify(bundle_details), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()
@item_bundle_management.route('/item-bundles', methods=['POST'])
@admin_role_required
def create_item_bundle():
    """
    Create Item Bundle
    This endpoint creates a new item bundle.
    ---
    tags:
      - Item Bundle Management
    parameters:
      - name: body
        in: body
        required: true
        schema:
          $ref: '#/definitions/ItemBundleCreate'
    responses:
      201:
        description: Item bundle created successfully.
      400:
        description: Invalid request data.
      500:
        description: Internal server error.
    definitions:
      ItemBundleCreate:
        type: object
        required:
          - bundle_name
          - item_ids
        properties:
          bundle_name:
            type: string
          description:
            type: string
          silver_price:
            type: integer
          gold_price:
            type: integer
          item_ids:
            type: array
            items:
              type: integer
    """
    session = Session()
    try:
        data = request.get_json()
        bundle_name = data.get('bundle_name')
        description = data.get('description')
        silver_price = data.get('silver_price')
        gold_price = data.get('gold_price')
        item_ids = data.get('item_ids')
        if not bundle_name or not item_ids:
            return jsonify({'error': 'Missing required fields'}), 400
        new_bundle = ItemBundle(bundle_name=bundle_name, description=description, silver_price=silver_price, gold_price=gold_price)
        session.add(new_bundle)
        session.commit()
        for item_id in item_ids:
            bundle_item = BundleItemAssociation(bundle_id=new_bundle.bundle_id, item_id=item_id)
            session.add(bundle_item)
        session.commit()
        return jsonify({'success': 'Item bundle created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()
@item_bundle_management.route('/item-bundles/<int:bundle_id>', methods=['PUT'])
@admin_role_required
def update_item_bundle(bundle_id):
    """
    Update Item Bundle
    This endpoint updates an existing item bundle.
    ---
    tags:
      - Item Bundle Management
    parameters:
      - name: bundle_id
        in: path
        description: ID of the item bundle.
        required: true
        type: integer
      - name: body
        in: body
        required: true
        schema:
          $ref: '#/definitions/ItemBundleUpdate'
    responses:
      200:
        description: Item bundle updated successfully.
      400:
        description: Invalid request data.
      404:
        description: Item bundle not found.
      500:
        description: Internal server error.
    definitions:
      ItemBundleUpdate:
        type: object
        properties:
          bundle_name:
            type: string
          description:
            type: string
          silver_price:
            type: integer
          gold_price:
            type: integer
          item_ids:
            type: array
            items:
              type: integer
    """
    session = Session()
    try:
        item_bundle = session.query(ItemBundle).filter_by(bundle_id=bundle_id).first()
        if not item_bundle:
            return jsonify({'error': 'Item bundle not found'}), 404
        data = request.get_json()
        bundle_name = data.get('bundle_name')
        description = data.get('description')
        silver_price = data.get('silver_price')
        gold_price = data.get('gold_price')
        item_ids = data.get('item_ids')
        if bundle_name:
            item_bundle.bundle_name = bundle_name
        if description:
            item_bundle.description = description
        if silver_price:
            item_bundle.silver_price = silver_price
        if gold_price:
            item_bundle.gold_price = gold_price
        if item_ids:
            session.query(BundleItemAssociation).filter_by(bundle_id=bundle_id).delete()
            for item_id in item_ids:
                bundle_item = BundleItemAssociation(bundle_id=bundle_id, item_id=item_id)
                session.add(bundle_item)
        session.commit()
        return jsonify({'success': 'Item bundle updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()
@item_bundle_management.route('/item-bundles/<int:bundle_id>', methods=['DELETE'])
@admin_role_required
def delete_item_bundle(bundle_id):
    """
    Delete Item Bundle
    This endpoint deletes an item bundle.
    ---
    tags:
      - Item Bundle Management
    parameters:
      - name: bundle_id
        in: path
        description: ID of the item bundle.
        required: true
        type: integer
    responses:
      200:
        description: Item bundle deleted successfully.
      404:
        description: Item bundle not found.
      500:
        description: Internal server error.
    """
    session = Session()
    try:
        item_bundle = session.query(ItemBundle).filter_by(bundle_id=bundle_id).first()
        if not item_bundle:
            return jsonify({'error': 'Item bundle not found'}), 404
        session.delete(item_bundle)
        session.commit()
        return jsonify({'success': 'Item bundle deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()