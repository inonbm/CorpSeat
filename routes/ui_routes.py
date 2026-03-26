from flask import Blueprint, request, redirect, render_template, g, url_for
from services import office_service, employee_service

ui_bp = Blueprint('ui', __name__, url_prefix='/ui')

@ui_bp.route('/offices', methods=['GET'])
def list_offices():
    filter_type = request.args.get('filter_type', '')
    sort_field = request.args.get('sort', 'id')
    sort_order = request.args.get('order', 'asc')
    page = int(request.args.get('page', 1))
    limit = 10
    
    if sort_field not in ['id', 'floor', 'room_number', 'employee_count']:
        sort_field = 'id'
    if sort_order not in ['asc', 'desc']:
        sort_order = 'asc'
        
    offices = office_service.get_offices_list(g.db, filter_type or None, sort_field, sort_order)
    total = len(offices)
    total_pages = (total + limit - 1) // limit if total > 0 else 1
    page = max(1, min(page, total_pages))
    start = (page - 1) * limit
    paginated = offices[start:start+limit]
    
    return render_template('offices/list.html', offices=paginated, page=page, total_pages=total_pages, qs=request.args)

@ui_bp.route('/offices/new', methods=['GET'])
def new_office():
    return render_template('offices/form.html', office=None)

@ui_bp.route('/offices', methods=['POST'])
def create_office():
    floor = int(request.form.get('floor'))
    room = int(request.form.get('room_number'))
    cap = int(request.form.get('capacity'))
    office_service.create_office(g.db, floor, room, cap)
    g.db.commit()
    return redirect(url_for('ui.list_offices'))

@ui_bp.route('/offices/<int:office_id>', methods=['GET'])
def get_office(office_id):
    from dal import office_dal, employee_dal
    from services.employee_service import _calculate_seniority
    office = office_dal.get_office_with_stats(g.db, office_id)
    raw_emps = employee_dal.get_employees_by_office(g.db, office_id)
    emps = []
    for e in raw_emps:
        ed = dict(e)
        ed['seniority'] = _calculate_seniority(ed['hire_date'])
        emps.append(ed)
    return render_template('offices/details.html', office=office, employees=emps)

@ui_bp.route('/offices/<int:office_id>/edit', methods=['GET'])
def edit_office(office_id):
    from dal import office_dal
    office = office_dal.get_office_with_stats(g.db, office_id)
    return render_template('offices/form.html', office=office)

@ui_bp.route('/offices/<int:office_id>/edit', methods=['POST'])
def update_office(office_id):
    floor = int(request.form.get('floor'))
    room = int(request.form.get('room_number'))
    cap = int(request.form.get('capacity'))
    office_service.update_office(g.db, office_id, floor, room, cap)
    g.db.commit()
    return redirect(url_for('ui.get_office', office_id=office_id))

@ui_bp.route('/offices/<int:office_id>/delete', methods=['POST'])
def delete_office(office_id):
    office_service.delete_office(g.db, office_id)
    g.db.commit()
    return redirect(url_for('ui.list_offices'))

@ui_bp.route('/employees', methods=['GET'])
def list_employees():
    filter_type = request.args.get('filter_type', '')
    dept = request.args.get('department', '')
    min_sen = request.args.get('min_seniority')
    max_sen = request.args.get('max_seniority')
    sort_field = request.args.get('sort', 'id')
    sort_order = request.args.get('order', 'asc')
    page = int(request.args.get('page', 1))
    limit = 10
    
    try:
        min_sen_val = int(min_sen) if min_sen else None
    except ValueError:
        min_sen_val = None
    try:
        max_sen_val = int(max_sen) if max_sen else None
    except ValueError:
        max_sen_val = None
        
    emps = employee_service.get_employees_list(
        g.db, filter_type or None, dept or None, min_sen_val, max_sen_val, sort_field, sort_order
    )
    
    total = len(emps)
    total_pages = (total + limit - 1) // limit if total > 0 else 1
    page = max(1, min(page, total_pages))
    start = (page - 1) * limit
    paginated = emps[start:start+limit]
    
    return render_template('employees/list.html', employees=paginated, page=page, total_pages=total_pages, qs=request.args)

@ui_bp.route('/employees/new', methods=['GET'])
def new_employee():
    from dal import office_dal
    offices = office_dal.get_all_offices(g.db)
    return render_template('employees/form.html', employee=None, offices=offices)

@ui_bp.route('/employees', methods=['POST'])
def create_employee():
    name = request.form.get('name')
    dept = request.form.get('department')
    hire = request.form.get('hire_date')
    sal = float(request.form.get('salary'))
    off_id = request.form.get('office_id')
    office_id = int(off_id) if off_id else None
    employee_service.create_employee(g.db, name, dept, hire, sal, office_id)
    g.db.commit()
    return redirect(url_for('ui.list_employees'))

@ui_bp.route('/employees/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    emp = employee_service.get_employee_extended(g.db, employee_id)
    return render_template('employees/details.html', employee=emp)

@ui_bp.route('/employees/<int:employee_id>/edit', methods=['GET'])
def edit_employee(employee_id):
    emp = employee_service.get_employee_extended(g.db, employee_id)
    from dal import office_dal
    offices = office_dal.get_all_offices(g.db)
    return render_template('employees/form.html', employee=emp, offices=offices)

@ui_bp.route('/employees/<int:employee_id>/edit', methods=['POST'])
def update_employee(employee_id):
    name = request.form.get('name')
    dept = request.form.get('department')
    hire = request.form.get('hire_date')
    sal = float(request.form.get('salary'))
    off_id = request.form.get('office_id')
    office_id = int(off_id) if off_id else None
    employee_service.update_employee(g.db, employee_id, name, dept, hire, sal, office_id)
    g.db.commit()
    return redirect(url_for('ui.get_employee', employee_id=employee_id))

@ui_bp.route('/employees/<int:employee_id>/delete', methods=['POST'])
def delete_employee(employee_id):
    employee_service.delete_employee(g.db, employee_id)
    g.db.commit()
    return redirect(url_for('ui.list_employees'))

@ui_bp.route('/assign', methods=['GET'])
def assign_ui():
    from dal import office_dal
    offices = office_dal.get_offices_with_stats(g.db)
    emps = employee_service.get_employees_list(g.db, sort_field='name')
    return render_template('offices/assign.html', offices=offices, employees=emps)

@ui_bp.route('/assign', methods=['POST'])
def process_assign():
    office_id = int(request.form.get('office_id'))
    emp_ids = request.form.getlist('employee_ids')
    employee_ids = [int(eid) for eid in emp_ids]
    office_service.assign_employees_to_office(g.db, office_id, employee_ids)
    return redirect(url_for('ui.get_office', office_id=office_id))
