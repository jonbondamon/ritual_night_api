from flask import Blueprint, request, jsonify
from app.routes import admin_role_required
from app.models import Session, Chroma, Item

chroma_management = Blueprint('chroma_management', __name__, url_prefix='/api')

@chroma_management.route('/chromas', methods=['GET'])
def get_all_chromas():
    """
    Get All Chromas
    This endpoint retrieves all chromas.
    ---
    tags:
      - Chroma Management
    responses:
      200:
        description: List of all chromas.
        schema:
          type: array
          items:
            $ref: '#/definitions/Chroma'
      500:
        description: Internal server error.
    definitions:
      Chroma:
        type: object
        properties:
          chroma_id:
            type: integer
          item_id:
            type: integer
          chroma_name:
            type: string
          required_prestige_level:
            type: integer
          required_item_level:
            type: integer
          silver_price:
            type: integer
          gold_price:
            type: integer
    """
    session = Session()
    try:
        chromas = session.query(Chroma).all()
        chroma_list = [
            {
                'chroma_id': chroma.chroma_id,
                'item_id': chroma.item_id,
                'chroma_name': chroma.chroma_name,
                'required_prestige_level': chroma.required_prestige_level,
                'required_item_level': chroma.required_item_level,
                'silver_price': chroma.silver_price,
                'gold_price': chroma.gold_price
            } for chroma in chromas
        ]
        return jsonify(chroma_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@chroma_management.route('/chromas/<int:chroma_id>', methods=['GET'])
def get_chroma(chroma_id):
    """
    Get Chroma
    This endpoint retrieves a specific chroma by ID.
    ---
    tags:
      - Chroma Management
    parameters:
      - name: chroma_id
        in: path
        description: ID of the chroma to retrieve.
        required: true
        type: integer
    responses:
      200:
        description: Chroma details.
        schema:
          $ref: '#/definitions/Chroma'
      404:
        description: Chroma not found.
      500:
        description: Internal server error.
    """
    session = Session()
    try:
        chroma = session.query(Chroma).filter_by(chroma_id=chroma_id).first()
        if chroma:
            chroma_data = {
                'chroma_id': chroma.chroma_id,
                'item_id': chroma.item_id,
                'chroma_name': chroma.chroma_name,
                'required_prestige_level': chroma.required_prestige_level,
                'required_item_level': chroma.required_item_level,
                'silver_price': chroma.silver_price,
                'gold_price': chroma.gold_price
            }
            return jsonify(chroma_data), 200
        else:
            return jsonify({'error': 'Chroma not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@chroma_management.route('/chromas', methods=['POST'])
@admin_role_required
def create_chroma():
    """
    Create Chroma
    This endpoint creates a new chroma.
    ---
    tags:
      - Chroma Management
    parameters:
      - name: body
        in: body
        description: Chroma details.
        required: true
        schema:
          $ref: '#/definitions/ChromaCreate'
    responses:
      201:
        description: Chroma created successfully.
      400:
        description: Invalid request data.
      500:
        description: Internal server error.
    definitions:
      ChromaCreate:
        type: object
        properties:
          item_id:
            type: integer
          chroma_name:
            type: string
          required_prestige_level:
            type: integer
          required_item_level:
            type: integer
          silver_price:
            type: integer
          gold_price:
            type: integer
        required:
          - item_id
          - chroma_name
          - required_prestige_level
          - required_item_level
          - silver_price
          - gold_price
    """
    session = Session()
    try:
        data = request.get_json()
        item_id = data.get('item_id')
        chroma_name = data.get('chroma_name')
        required_prestige_level = data.get('required_prestige_level')
        required_item_level = data.get('required_item_level')
        silver_price = data.get('silver_price')
        gold_price = data.get('gold_price')

        if not all([item_id, chroma_name, required_prestige_level, required_item_level, silver_price, gold_price]):
            return jsonify({'error': 'Invalid request data'}), 400

        item = session.query(Item).filter_by(item_id=item_id).first()
        if not item:
            return jsonify({'error': 'Item not found'}), 404

        new_chroma = Chroma(
            item_id=item_id,
            chroma_name=chroma_name,
            required_prestige_level=required_prestige_level,
            required_item_level=required_item_level,
            silver_price=silver_price,
            gold_price=gold_price
        )
        session.add(new_chroma)
        session.commit()
        return jsonify({'success': 'Chroma created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@chroma_management.route('/chromas/<int:chroma_id>', methods=['PUT'])
@admin_role_required
def update_chroma(chroma_id):
    """
    Update Chroma
    This endpoint updates a chroma.
    ---
    tags:
      - Chroma Management
    parameters:
      - name: chroma_id
        in: path
        description: ID of the chroma to update.
        required: true
        type: integer
      - name: body
        in: body
        description: Updated chroma details.
        required: true
        schema:
          $ref: '#/definitions/ChromaUpdate'
    responses:
      200:
        description: Chroma updated successfully.
      400:
        description: Invalid request data.
      404:
        description: Chroma not found.
      500:
        description: Internal server error.
    definitions:
      ChromaUpdate:
        type: object
        properties:
          item_id:
            type: integer
          chroma_name:
            type: string
          required_prestige_level:
            type: integer
          required_item_level:
            type: integer
          silver_price:
            type: integer
          gold_price:
            type: integer
    """
    session = Session()
    try:
        chroma = session.query(Chroma).filter_by(chroma_id=chroma_id).first()
        if not chroma:
            return jsonify({'error': 'Chroma not found'}), 404

        data = request.get_json()
        item_id = data.get('item_id')
        chroma_name = data.get('chroma_name')
        required_prestige_level = data.get('required_prestige_level')
        required_item_level = data.get('required_item_level')
        silver_price = data.get('silver_price')
        gold_price = data.get('gold_price')

        if item_id:
            item = session.query(Item).filter_by(item_id=item_id).first()
            if not item:
                return jsonify({'error': 'Item not found'}), 404
            chroma.item_id = item_id

        if chroma_name:
            chroma.chroma_name = chroma_name
        if required_prestige_level:
            chroma.required_prestige_level = required_prestige_level
        if required_item_level:
            chroma.required_item_level = required_item_level
        if silver_price:
            chroma.silver_price = silver_price
        if gold_price:
            chroma.gold_price = gold_price

        session.commit()
        return jsonify({'success': 'Chroma updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@chroma_management.route('/chromas/<int:chroma_id>', methods=['DELETE'])
@admin_role_required
def delete_chroma(chroma_id):
    """
    Delete Chroma
    This endpoint deletes a chroma.
    ---
    tags:
      - Chroma Management
    parameters:
      - name: chroma_id
        in: path
        description: ID of the chroma to delete.
        required: true
        type: integer
    responses:
      200:
        description: Chroma deleted successfully.
      404:
        description: Chroma not found.
      500:
        description: Internal server error.
    """
    session = Session()
    try:
        chroma = session.query(Chroma).filter_by(chroma_id=chroma_id).first()
        if not chroma:
            return jsonify({'error': 'Chroma not found'}), 404

        session.delete(chroma)
        session.commit()
        return jsonify({'success': 'Chroma deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()