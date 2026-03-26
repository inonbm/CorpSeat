from flask import Blueprint, request, jsonify, g
from services import office_service, employee_service

api_bp = Blueprint('api', __name__, url_prefix='/api')

def std_response(data, page=1, limit=10, total=0):
    total_pages = (total + limit - 1) // limit if limit > 0 else 0
    return jsonify({
        "data": data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages
        }
    })

def err_response(code, message, details=None):
    res = {"error": {"code": code, "message": message}}
    if details:
        res["error"]["details"] = details
    return jsonify(res), code

@api_bp.route('/offices', methods=['GET'])
def get_offices():
    filter_type = request.args.get('filter')
    sort_field = request.args.get('sort', 'id')
    sort_order = request.args.get('order', 'asc').lower()
    
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
    except ValueError:
        return err_response(400, "Invalid pagination parameters")

    if limit <= 0:
        return err_response(400, "limit must be > 0")
    if sort_field not in ['id', 'floor', 'room_number', 'employee_count']:
        return err_response(400, "Invalid sort field")
    if sort_order not in ['asc', 'desc']:
        return err_response(400, "Invalid order field")

    offices = office_service.get_offices_list(g.db, filter_type, sort_field, sort_order)
    total = len(offices)
    total_pages = (total + limit - 1) // limit
    
    if page > total_pages and total_pages > 0:
        return std_response([], page, limit, total)
        
    start = (page - 1) * limit
    end = start + limit
    return std_response(offices[start:end], page, limit, total)

@api_bp.route('/offices/<int:office_id>', methods=['GET'])
def get_office(office_id):
    from dal import office_dal
    office = office_dal.get_office_with_stats(g.db, office_id)
    if not office:
        return err_response(404, "Office not found")
    return jsonify(office)

@api_bp.route('/offices/<int:office_id>/employees', methods=['GET'])
def get_office_employees(office_id):
    from dal import employee_dal
    emps = employee_dal.get_employees_by_office(g.db, office_id)
    result = []
    from services.employee_service import _calculate_seniority
    for e in emps:
        ed = dict(e)
        ed['seniority'] = _calculate_seniority(ed['hire_date'])
        result.append(ed)
    return jsonify(result)

@api_bp.route('/offices', methods=['POST'])
def create_office():
    data = request.json or {}
    try:
        o_id = office_service.create_office(g.db, data.get('floor'), data.get('room_number'), data.get('capacity'))
        g.db.commit()
        return jsonify({"id": o_id}), 201
    except Exception as e:
        g.db.rollback()
        return err_response(400, str(e))

@api_bp.route('/offices/<int:office_id>', methods=['PUT'])
def update_office(office_id):
    data = request.json or {}
    try:
        office_service.update_office(g.db, office_id, data.get('floor'), data.get('room_number'), data.get('capacity'))
        g.db.commit()
        return jsonify({"success": True})
    except Exception as e:
        g.db.rollback()
        return err_response(400, str(e))

@api_bp.route('/offices/<int:office_id>', methods=['DELETE'])
def delete_office(office_id):
    try:
        rows = office_service.delete_office(g.db, office_id)
        if rows == 0:
            return err_response(404, "Office not found")
        g.db.commit()
        return jsonify({"success": True})
    except Exception as e:
        g.db.rollback()
        return err_response(400, str(e))

@api_bp.route('/employees', methods=['GET'])
def get_employees():
    filter_type = request.args.get('filter')
    dept = request.args.get('department')
    sort_field = request.args.get('sort', 'id')
    sort_order = request.args.get('order', 'asc').lower()
    
    try:
        min_sen = int(request.args.get('min_seniority')) if request.args.get('min_seniority') else None
        max_sen = int(request.args.get('max_seniority')) if request.args.get('max_seniority') else None
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
    except ValueError:
        return err_response(400, "Invalid parameter type")

    if limit <= 0:
        return err_response(400, "limit must be > 0")
    if sort_field not in ['id', 'name', 'seniority', 'department']:
        return err_response(400, "Invalid sort field")
    if sort_order not in ['asc', 'desc']:
        return err_response(400, "Invalid order field")

    emps = employee_service.get_employees_list(g.db, filter_type, dept, min_sen, max_sen, sort_field, sort_order)
    total = len(emps)
    total_pages = (total + limit - 1) // limit
    
    if page > total_pages and total_pages > 0:
        return std_response([], page, limit, total)
        
    start = (page - 1) * limit
    return std_response(emps[start:start+limit], page, limit, total)

@api_bp.route('/employees/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    emp = employee_service.get_employee_extended(g.db, employee_id)
    if not emp:
        return err_response(404, "Employee not found")
    return jsonify(emp)

@api_bp.route('/employees', methods=['POST'])
def create_employee():
    data = request.json or {}
    try:
        e_id = employee_service.create_employee(g.db, data.get('name'), data.get('department'), data.get('hire_date'), data.get('salary'), data.get('office_id'))
        g.db.commit()
        return jsonify({"id": e_id}), 201
    except Exception as e:
        g.db.rollback()
        return err_response(400, str(e))

@api_bp.route('/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    data = request.json or {}
    try:
        employee_service.update_employee(g.db, employee_id, data.get('name'), data.get('department'), data.get('hire_date'), data.get('salary'), data.get('office_id'))
        g.db.commit()
        return jsonify({"success": True})
    except Exception as e:
        g.db.rollback()
        return err_response(400, str(e))

@api_bp.route('/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    try:
        rows = employee_service.delete_employee(g.db, employee_id)
        if rows == 0:
            return err_response(404, "Employee not found")
        g.db.commit()
        return jsonify({"success": True})
    except Exception as e:
        g.db.rollback()
        return err_response(400, str(e))

@api_bp.route('/assign', methods=['POST'])
def assign():
    data = request.json or {}
    try:
        office_id = data.get('office_id')
        employee_ids = data.get('employee_ids', [])
        if not isinstance(employee_ids, list):
            return err_response(400, "employee_ids must be a list")
            
        office_service.assign_employees_to_office(g.db, office_id, employee_ids)
        # Note: commit is handled successfully inside assign_employees_to_office via atomic logic
        return jsonify({"success": True})
    except Exception as e:
        # rollback already safely triggered inside service if failed
        return err_response(400, str(e))
