from flask import Blueprint, request, jsonify
from app.models import Session, Shader, Item
from app.routes import admin_role_required

shader_management = Blueprint('shader_management', __name__, url_prefix='/api')

@shader_management.route('/shaders', methods=['GET'])
def get_all_shaders():
    """
    Get All Shaders
    This endpoint retrieves all shaders.
    ---
    tags:
      - Shader Management
    responses:
      200:
        description: List of all shaders.
        schema:
          type: array
          items:
            $ref: '#/definitions/Shader'
      500:
        description: Internal server error.
    definitions:
      Shader:
        type: object
        properties:
          shader_id:
            type: integer
          item_id:
            type: integer
          shader_name:
            type: string
          required_prestige_level:
            type: integer
          required_item_level:
            type: integer
          shader_type:
            type: string
          silver_price:
            type: integer
          gold_price:
            type: integer
    """
    session = Session()
    try:
        shaders = session.query(Shader).all()
        shader_list = [
            {
                'shader_id': shader.shader_id,
                'item_id': shader.item_id,
                'shader_name': shader.shader_name,
                'required_prestige_level': shader.required_prestige_level,
                'required_item_level': shader.required_item_level,
                'shader_type': shader.shader_type,
                'silver_price': shader.silver_price,
                'gold_price': shader.gold_price
            } for shader in shaders
        ]
        return jsonify(shader_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@shader_management.route('/shaders/<int:shader_id>', methods=['GET'])
def get_shader(shader_id):
    """
    Get Shader
    This endpoint retrieves a specific shader by ID.
    ---
    tags:
      - Shader Management
    parameters:
      - name: shader_id
        in: path
        description: ID of the shader to retrieve.
        required: true
        type: integer
    responses:
      200:
        description: Shader details.
        schema:
          $ref: '#/definitions/Shader'
      404:
        description: Shader not found.
      500:
        description: Internal server error.
    """
    session = Session()
    try:
        shader = session.query(Shader).filter_by(shader_id=shader_id).first()
        if shader:
            shader_data = {
                'shader_id': shader.shader_id,
                'item_id': shader.item_id,
                'shader_name': shader.shader_name,
                'required_prestige_level': shader.required_prestige_level,
                'required_item_level': shader.required_item_level,
                'shader_type': shader.shader_type,
                'silver_price': shader.silver_price,
                'gold_price': shader.gold_price
            }
            return jsonify(shader_data), 200
        else:
            return jsonify({'error': 'Shader not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@shader_management.route('/shaders', methods=['POST'])
@admin_role_required
def create_shader():
    """
    Create Shader
    This endpoint creates a new shader.
    ---
    tags:
      - Shader Management
    parameters:
      - name: body
        in: body
        required: true
        schema:
          $ref: '#/definitions/ShaderCreate'
    responses:
      201:
        description: Shader created successfully.
      400:
        description: Bad request.
      500:
        description: Internal server error.
    definitions:
      ShaderCreate:
        type: object
        required:
          - item_id
          - shader_name
          - required_prestige_level
          - required_item_level
          - shader_type
          - silver_price
          - gold_price
        properties:
          item_id:
            type: integer
          shader_name:
            type: string
          required_prestige_level:
            type: integer
          required_item_level:
            type: integer
          shader_type:
            type: string
          silver_price:
            type: integer
          gold_price:
            type: integer
    """
    session = Session()
    try:
        data = request.get_json()
        item_id = data.get('item_id')
        shader_name = data.get('shader_name')
        required_prestige_level = data.get('required_prestige_level')
        required_item_level = data.get('required_item_level')
        shader_type = data.get('shader_type')
        silver_price = data.get('silver_price')
        gold_price = data.get('gold_price')

        if not all([item_id, shader_name, required_prestige_level, required_item_level, shader_type, silver_price, gold_price]):
            return jsonify({'error': 'Missing required fields'}), 400

        item = session.query(Item).filter_by(item_id=item_id).first()
        if not item:
            return jsonify({'error': 'Item not found'}), 404

        new_shader = Shader(
            item_id=item_id,
            shader_name=shader_name,
            required_prestige_level=required_prestige_level,
            required_item_level=required_item_level,
            shader_type=shader_type,
            silver_price=silver_price,
            gold_price=gold_price
        )
        session.add(new_shader)
        session.commit()
        return jsonify({'success': 'Shader created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@shader_management.route('/shaders/<int:shader_id>', methods=['PUT'])
@admin_role_required
def update_shader(shader_id):
    """
    Update Shader
    This endpoint updates a shader.
    ---
    tags:
      - Shader Management
    parameters:
      - name: shader_id
        in: path
        description: ID of the shader to update.
        required: true
        type: integer
      - name: body
        in: body
        required: true
        schema:
          $ref: '#/definitions/ShaderUpdate'
    responses:
      200:
        description: Shader updated successfully.
      400:
        description: Bad request.
      404:
        description: Shader not found.
      500:
        description: Internal server error.
    definitions:
      ShaderUpdate:
        type: object
        properties:
          item_id:
            type: integer
          shader_name:
            type: string
          required_prestige_level:
            type: integer
          required_item_level:
            type: integer
          shader_type:
            type: string
          silver_price:
            type: integer
          gold_price:
            type: integer
    """
    session = Session()
    try:
        shader = session.query(Shader).filter_by(shader_id=shader_id).first()
        if not shader:
            return jsonify({'error': 'Shader not found'}), 404

        data = request.get_json()
        item_id = data.get('item_id')
        shader_name = data.get('shader_name')
        required_prestige_level = data.get('required_prestige_level')
        required_item_level = data.get('required_item_level')
        shader_type = data.get('shader_type')
        silver_price = data.get('silver_price')
        gold_price = data.get('gold_price')

        if item_id:
            item = session.query(Item).filter_by(item_id=item_id).first()
            if not item:
                return jsonify({'error': 'Item not found'}), 404
            shader.item_id = item_id

        if shader_name:
            shader.shader_name = shader_name
        if required_prestige_level:
            shader.required_prestige_level = required_prestige_level
        if required_item_level:
            shader.required_item_level = required_item_level
        if shader_type:
            shader.shader_type = shader_type
        if silver_price:
            shader.silver_price = silver_price
        if gold_price:
            shader.gold_price = gold_price

        session.commit()
        return jsonify({'success': 'Shader updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@shader_management.route('/shaders/<int:shader_id>', methods=['DELETE'])
@admin_role_required
def delete_shader(shader_id):
    """
    Delete Shader
    This endpoint deletes a shader.
    ---
    tags:
      - Shader Management
    parameters:
      - name: shader_id
        in: path
        description: ID of the shader to delete.
        required: true
        type: integer
    responses:
      200:
        description: Shader deleted successfully.
      404:
        description: Shader not found.
      500:
        description: Internal server error.
    """
    session = Session()
    try:
        shader = session.query(Shader).filter_by(shader_id=shader_id).first()
        if not shader:
            return jsonify({'error': 'Shader not found'}), 404

        session.delete(shader)
        session.commit()
        return jsonify({'success': 'Shader deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()