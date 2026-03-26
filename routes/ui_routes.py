from flask import Blueprint, request, redirect, render_template

ui_bp = Blueprint('ui', __name__, url_prefix='/ui')

# Dummy UI render for Phase 5 scope. Full layout arrives in Phase 6.
@ui_bp.route('/offices', methods=['GET'])
def list_offices(): return "<html><body>HTML ONLY</body></html>"

@ui_bp.route('/offices', methods=['POST'])
def create_office(): return redirect('/ui/offices')

@ui_bp.route('/employees', methods=['GET'])
def list_employees(): return "<html><body>HTML ONLY</body></html>"

@ui_bp.route('/employees', methods=['POST'])
def create_employee(): return redirect('/ui/employees')
