from flask import Blueprint, request, jsonify
from app.routes import admin_role_required
from app.models import Session, PremiumStoreSchedule, PremiumStoreSet
from datetime import datetime

premium_store_schedule_management = Blueprint('premium_store_schedule', __name__)

@premium_store_schedule_management.route('/api/premium-store-schedules', methods=['GET'])
def get_all_premium_store_schedules():
    """
    Get All Premium Store Schedules
    This endpoint retrieves all premium store schedules.
    ---
    tags:
      - Premium Store Schedule Management
    responses:
      200:
        description: List of all premium store schedules.
        examples:
          application/json: [{"schedule_id": 1, "set_id": 1, "start_date": "2023-06-01T00:00:00", "end_date": "2023-06-30T23:59:59"}]
      500:
        description: Internal server error, if any exception occurs.
        examples:
          application/json: {"error": "Failed to fetch premium store schedules", "details": "<exception details>"}
    """
    session = Session()
    try:
        schedules = session.query(PremiumStoreSchedule).all()
        schedules_list = [
            {"schedule_id": schedule.schedule_id, "set_id": schedule.set_id,
             "start_date": schedule.start_date.isoformat(), "end_date": schedule.end_date.isoformat()}
            for schedule in schedules
        ]
        return jsonify(schedules_list), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch premium store schedules', 'details': str(e)}), 500
    finally:
        session.close()

@premium_store_schedule_management.route('/api/premium-store-schedules/<int:schedule_id>', methods=['GET'])
def get_premium_store_schedule(schedule_id):
    """
    Get Premium Store Schedule
    This endpoint retrieves a specific premium store schedule by ID.
    ---
    tags:
      - Premium Store Schedule Management
    parameters:
      - in: path
        name: schedule_id
        description: ID of the premium store schedule to retrieve
        required: true
        type: integer
    responses:
      200:
        description: Premium store schedule details.
        examples:
          application/json: {"schedule_id": 1, "set_id": 1, "start_date": "2023-06-01T00:00:00", "end_date": "2023-06-30T23:59:59"}
      404:
        description: Premium store schedule not found.
        examples:
          application/json: {"error": "Premium store schedule not found"}
      500:
        description: Internal server error, if any exception occurs.
        examples:
          application/json: {"error": "Failed to fetch premium store schedule", "details": "<exception details>"}
    """
    session = Session()
    try:
        schedule = session.query(PremiumStoreSchedule).filter_by(schedule_id=schedule_id).first()
        if schedule:
            schedule_data = {"schedule_id": schedule.schedule_id, "set_id": schedule.set_id,
                             "start_date": schedule.start_date.isoformat(), "end_date": schedule.end_date.isoformat()}
            return jsonify(schedule_data), 200
        else:
            return jsonify({'error': 'Premium store schedule not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Failed to fetch premium store schedule', 'details': str(e)}), 500
    finally:
        session.close()

@premium_store_schedule_management.route('/api/premium-store-schedules', methods=['POST'])
@admin_role_required
def create_premium_store_schedule():
    """
    Create Premium Store Schedule
    This endpoint creates a new premium store schedule.
    ---
    tags:
      - Premium Store Schedule Management
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        description: Premium store schedule details
        required: true
        schema:
          type: object
          properties:
            set_id:
              type: integer
              description: ID of the premium store set
            start_date:
              type: string
              format: date-time
              description: Start date and time of the schedule
            end_date:
              type: string
              format: date-time
              description: End date and time of the schedule
    responses:
      201:
        description: Premium store schedule created successfully.
        examples:
          application/json: {"success": "Premium store schedule created successfully", "schedule_id": 1}
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
          application/json: {"error": "Failed to create premium store schedule", "details": "<exception details>"}
    """
    session = Session()
    try:
        data = request.get_json()
        set_id = data.get('set_id')
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')

        if not set_id or not start_date_str or not end_date_str:
            return jsonify({'error': 'Missing required fields'}), 400

        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)

        premium_store_set = session.query(PremiumStoreSet).filter_by(set_id=set_id).first()
        if not premium_store_set:
            return jsonify({'error': 'Premium store set not found'}), 404

        new_schedule = PremiumStoreSchedule(set_id=set_id, start_date=start_date, end_date=end_date)
        session.add(new_schedule)
        session.commit()

        return jsonify({'success': 'Premium store schedule created successfully', 'schedule_id': new_schedule.schedule_id}), 201
    except Exception as e:
        return jsonify({'error': 'Failed to create premium store schedule', 'details': str(e)}), 500
    finally:
        session.close()

@premium_store_schedule_management.route('/api/premium-store-schedules/<int:schedule_id>', methods=['PUT'])
@admin_role_required
def update_premium_store_schedule(schedule_id):
    """
    Update Premium Store Schedule
    This endpoint updates a premium store schedule.
    ---
    tags:
      - Premium Store Schedule Management
    security:
      - Bearer: []
    parameters:
      - in: path
        name: schedule_id
        description: ID of the premium store schedule to update
        required: true
        type: integer
      - in: body
        name: body
        description: Updated premium store schedule details
        required: true
        schema:
          type: object
          properties:
            set_id:
              type: integer
              description: ID of the premium store set
            start_date:
              type: string
              format: date-time
              description: Start date and time of the schedule
            end_date:
              type: string
              format: date-time
              description: End date and time of the schedule
    responses:
      200:
        description: Premium store schedule updated successfully.
        examples:
          application/json: {"success": "Premium store schedule updated successfully"}
      400:
        description: Bad request, if required fields are missing or invalid.
        examples:
          application/json: {"error": "Missing required fields"}
      404:
        description: Premium store schedule or set not found.
        examples:
          application/json: {"error": "Premium store schedule not found"}
      500:
        description: Internal server error, if any exception occurs.
        examples:
          application/json: {"error": "Failed to update premium store schedule", "details": "<exception details>"}
    """
    session = Session()
    try:
        data = request.get_json()
        set_id = data.get('set_id')
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')

        if not set_id or not start_date_str or not end_date_str:
            return jsonify({'error': 'Missing required fields'}), 400

        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)

        schedule = session.query(PremiumStoreSchedule).filter_by(schedule_id=schedule_id).first()
        if not schedule:
            return jsonify({'error': 'Premium store schedule not found'}), 404

        premium_store_set = session.query(PremiumStoreSet).filter_by(set_id=set_id).first()
        if not premium_store_set:
            return jsonify({'error': 'Premium store set not found'}), 404

        schedule.set_id = set_id
        schedule.start_date = start_date
        schedule.end_date = end_date
        session.commit()

        return jsonify({'success': 'Premium store schedule updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to update premium store schedule', 'details': str(e)}), 500
    finally:
        session.close()

@premium_store_schedule_management.route('/api/premium-store-schedules/<int:schedule_id>', methods=['DELETE'])
@admin_role_required
def delete_premium_store_schedule(schedule_id):
    """
    Delete Premium Store Schedule
    This endpoint deletes a premium store schedule.
    ---
    tags:
      - Premium Store Schedule Management
    security:
      - Bearer: []
    parameters:
      - in: path
        name: schedule_id
        description: ID of the premium store schedule to delete
        required: true
        type: integer
    responses:
      200:
        description: Premium store schedule deleted successfully.
        examples:
          application/json: {"success": "Premium store schedule deleted successfully"}
      404:
        description: Premium store schedule not found.
        examples:
          application/json: {"error": "Premium store schedule not found"}
      500:
        description: Internal server error, if any exception occurs.
        examples:
          application/json: {"error": "Failed to delete premium store schedule", "details": "<exception details>"}
    """
    session = Session()
    try:
        schedule = session.query(PremiumStoreSchedule).filter_by(schedule_id=schedule_id).first()
        if not schedule:
            return jsonify({'error': 'Premium store schedule not found'}), 404

        session.delete(schedule)
        session.commit()

        return jsonify({'success': 'Premium store schedule deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to delete premium store schedule', 'details': str(e)}), 500
    finally:
        session.close()