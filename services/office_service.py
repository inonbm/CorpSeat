from dal import office_dal, employee_dal

def _validate_office(capacity):
    if int(capacity) <= 0:
        raise ValueError("capacity must be > 0")

def create_office(conn, floor, room_number, capacity):
    _validate_office(capacity)
    return office_dal.create_office(conn, floor, room_number, capacity)

def update_office(conn, office_id, floor, room_number, capacity):
    _validate_office(capacity)
    return office_dal.update_office(conn, office_id, floor, room_number, capacity)

def get_office(conn, office_id):
    return office_dal.get_office(conn, office_id)

def get_all_offices(conn):
    return office_dal.get_all_offices(conn)

def delete_office(conn, office_id):
    return office_dal.delete_office(conn, office_id)

def assign_employees_to_office(conn, office_id, employee_ids):
    if not employee_ids:
        return
        
    try:
        # Business Rule: Validate ALL employee_ids exist before making any change
        found_records = employee_dal.get_employees_by_ids(conn, employee_ids)
        found_ids = {row['id'] for row in found_records}
        unique_requested_ids = set(employee_ids)
        
        if len(found_ids) != len(unique_requested_ids):
            raise ValueError("One or more employee IDs do not exist.")
            
        # Business Rule: If employee is already in same office -> no-op 
        # Business Rule: If different office -> Reassign securely
        for emp_record in found_records:
            emp_id = emp_record['id']
            curr_office_id = emp_record['office_id']
            if curr_office_id == office_id:
                continue
            
            try:
                employee_dal.update_employee_office(conn, emp_id, office_id)
            except Exception as e:
                raise ValueError("Foreign key violation or DB error during assignment: " + str(e))
                
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
