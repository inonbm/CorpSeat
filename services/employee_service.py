from datetime import date, datetime
from dal import employee_dal

def _calculate_seniority(hire_date_str):
    hire_date = datetime.strptime(hire_date_str, "%Y-%m-%d").date()
    today = date.today()
    delta = today - hire_date
    return max(0, int(delta.days // 365))

def _validate_employee(hire_date_str, salary):
    hire_date = datetime.strptime(hire_date_str, "%Y-%m-%d").date()
    if hire_date > date.today():
        raise ValueError("hire_date must not be in the future")
    if float(salary) <= 0:
        raise ValueError("salary must be > 0")

def create_employee(conn, name, department, hire_date, salary, office_id=None):
    _validate_employee(hire_date, salary)
    return employee_dal.create_employee(conn, name, department, hire_date, salary, office_id)

def get_employee(conn, employee_id):
    emp = employee_dal.get_employee(conn, employee_id)
    if emp:
        emp_dict = dict(emp)
        emp_dict['seniority'] = _calculate_seniority(emp_dict['hire_date'])
        return emp_dict
    return None

def get_all_employees(conn):
    emps = employee_dal.get_all_employees(conn)
    result = []
    for emp in emps:
        emp_dict = dict(emp)
        emp_dict['seniority'] = _calculate_seniority(emp_dict['hire_date'])
        result.append(emp_dict)
    return result

def update_employee(conn, employee_id, name, department, hire_date, salary, office_id):
    _validate_employee(hire_date, salary)
    return employee_dal.update_employee(conn, employee_id, name, department, hire_date, salary, office_id)

def delete_employee(conn, employee_id):
    return employee_dal.delete_employee(conn, employee_id)


def get_employees_list(conn, filter_type=None, department=None, min_seniority=None, max_seniority=None, sort_field='id', sort_order='asc'):
    emps = employee_dal.get_all_employees_with_office(conn)
    result = []
    for e in emps:
        e['seniority'] = _calculate_seniority(e['hire_date'])
        result.append(e)
    
    if filter_type == 'unassigned':
        result = [e for e in result if e['office_id'] is None]
        
    if department:
        result = [e for e in result if e['department'].lower() == department.lower()]
        
    if min_seniority is not None:
        result = [e for e in result if e['seniority'] >= min_seniority]
        
    if max_seniority is not None:
        result = [e for e in result if e['seniority'] <= max_seniority]
        
    rev = (sort_order == 'desc')
    
    def safe_sort_key(x):
        val = x.get(sort_field)
        if val is None:
            return "" if isinstance(val, str) else 0
        if isinstance(val, str):
            return val.lower()
        return val
        
    result.sort(key=safe_sort_key, reverse=rev)
    return result

def get_employee_extended(conn, employee_id):
    emp = employee_dal.get_employee_with_office(conn, employee_id)
    if emp:
        emp['seniority'] = _calculate_seniority(emp['hire_date'])
        return emp
    return None
